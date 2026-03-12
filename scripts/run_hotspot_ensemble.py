"""
HPC batch script for processing wetland ensemble and extracting hotspots.
"""
import argparse
import logging
import time
from pathlib import Path
import xarray as xr
from dask.distributed import Client, performance_report

# Import pipeline components
from wetland_analysis.analysis.pipeline import WetlandEnsemblePipeline
from wetland_analysis.analysis.hotspots import HotspotAnalyzer
from wetland_analysis.data.satellite_fetcher import GEEFetcher

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="HPC Hotspot Extraction for Wetland Ensemble")
    
    # ROI
    parser.add_argument("--min_lon", type=float, required=True, help="Minimum longitude")
    parser.add_argument("--min_lat", type=float, required=True, help="Minimum latitude")
    parser.add_argument("--max_lon", type=float, required=True, help="Maximum longitude")
    parser.add_argument("--max_lat", type=float, required=True, help="Maximum latitude")
    
    # Time
    parser.add_argument("--start_date", type=str, default="2020-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end_date", type=str, default="2020-12-31", help="End date (YYYY-MM-DD)")
    
    # Dask & Output
    parser.add_argument("--dask_scheduler", type=str, default=None, help="Dask scheduler address (if using existing cluster)")
    parser.add_argument("--use_mpi", action="store_true", help="Use dask-mpi to initialize cluster")
    parser.add_argument("--output_zarr", type=str, default="results/hotspots_ensemble.zarr", help="Path to save Zarr output")
    parser.add_argument("--report_file", type=str, default="results/dask-report.html", help="Path to save Dask performance report")
    
    # Hotspot specific
    parser.add_argument("--num_hotspots", type=int, default=5, help="Number of hotspots to extract")
    parser.add_argument("--gee_folder", type=str, default="wetland_hotspots", help="GEE Export Drive Folder")
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    # 1. Setup Dask Client
    client = None
    if args.use_mpi:
        logger.info("Initializing Dask MPI...")
        try:
            from dask_mpi import initialize
            initialize()
            client = Client()
        except ImportError:
            logger.error("dask-mpi not installed. Run without --use_mpi or install it.")
            return
    elif args.dask_scheduler:
        logger.info(f"Connecting to Dask Scheduler at {args.dask_scheduler}")
        client = Client(args.dask_scheduler)
    else:
        logger.info("Starting local Dask cluster...")
        client = Client()
        
    logger.info(f"Dask Dashboard accessible at: {client.dashboard_link}")
    
    roi_bounds = (args.min_lon, args.min_lat, args.max_lon, args.max_lat)
    
    # Ensure output directories exist
    output_zarr_path = Path(args.output_zarr)
    output_zarr_path.parent.mkdir(parents=True, exist_exist=True)
    report_path = Path(args.report_file)
    report_path.parent.mkdir(parents=True, exist_exist=True)

    with performance_report(filename=str(report_path)):
        # 2. Run Pipeline
        logger.info(f"Initializing pipeline for ROI: {roi_bounds}")
        pipeline = WetlandEnsemblePipeline(
            roi_bounds=roi_bounds,
            start_date=args.start_date,
            end_date=args.end_date
        )
        
        # Add dummy datasets for demonstration. In reality, you'd configure paths here.
        # This assumes the aligner can handle lazy loading with Dask.
        logger.info("Adding datasets...")
        pipeline.add_dataset("gwd30", weight=0.8, mock=True) # Assuming mock kwarg for tests
        pipeline.add_dataset("glwd", weight=0.5, mock=True)
        
        logger.info("Running pipeline analysis...")
        results_ds = pipeline.run_analysis()
        
        # Optimize chunking before save/compute
        logger.info("Applying chunking strategy...")
        results_ds = results_ds.chunk({'lat': 1000, 'lon': 1000})
        
        logger.info(f"Saving results to {output_zarr_path}...")
        results_ds.to_zarr(output_zarr_path, mode='w', consolidated=True)
        
        # 3. Hotspot Analysis
        logger.info("Starting hotspot analysis...")
        # Reload from Zarr to ensure clean dask graph
        zarr_ds = xr.open_zarr(output_zarr_path, consolidated=True)
        
        analyzer = HotspotAnalyzer(window_size_deg=0.1)
        hotspots = analyzer.find_top_n_hotspots(
            entropy_da=zarr_ds['shannon_entropy'],
            n=args.num_hotspots
        )
        
        if not hotspots:
            logger.warning("No hotspots found. Exiting.")
            return
            
        # 4. GEE Fetching
        logger.info("Initializing GEE Fetcher...")
        try:
            fetcher = GEEFetcher()
            fetcher.batch_fetch_hotspots(
                hotspots=hotspots,
                start_date=args.start_date,
                end_date=args.end_date,
                folder_name=args.gee_folder
            )
        except Exception as e:
            logger.error(f"GEE Fetching failed: {e}")
            
    logger.info("HPC workflow complete.")
    if client:
        client.close()

if __name__ == "__main__":
    main()