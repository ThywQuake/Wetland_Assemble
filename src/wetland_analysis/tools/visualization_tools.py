"""
Visualization tools for AI agents.
"""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def create_map(
    dataset_name: str,
    year: int,
    output_path: str,
    title: Optional[str] = None,
    region: Optional[str] = None
) -> Dict:
    """
    Create a wetland distribution map.

    Args:
        dataset_name: Name of dataset to visualize
        year: Year for visualization
        output_path: Path to save the map
        title: Title for the map
        region: Region to visualize

    Returns:
        Dictionary with result status
    """
    from ..data.loader import load_wetland_dataset
    from ..data.preprocessing import mask_region
    from ..data.config import get_region_bbox
    from ..visualization.maps import plot_wetland_map

    try:
        # Load dataset
        logger.info(f"Loading {dataset_name} for map creation (year={year})")
        data = load_wetland_dataset(dataset_name, year=year)

        # Apply region mask if specified
        if region:
            try:
                bbox = get_region_bbox(region)
                data = mask_region(data, bbox)
            except ValueError:
                logger.warning(f"Region '{region}' not found, ignoring")

        # Create map
        if title is None:
            title = f"Wetland Distribution - {dataset_name} ({year})"

        fig = plot_wetland_map(
            data,
            title=title,
            save_path=output_path,
            show=False
        )

        # Close figure to free memory
        import matplotlib.pyplot as plt
        plt.close(fig)

        return {
            'success': True,
            'dataset': dataset_name,
            'year': year,
            'region': region,
            'output_path': output_path,
            'map_created': True
        }

    except Exception as e:
        logger.error(f"Error creating map: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def create_trend_visualization(
    dataset_name: str,
    start_year: int,
    end_year: int,
    output_path: str,
    region: Optional[str] = None
) -> Dict:
    """
    Create a visualization of temporal trends.

    Args:
        dataset_name: Name of dataset to visualize
        start_year: Start year
        end_year: End year
        output_path: Path to save visualization
        region: Region to visualize

    Returns:
        Dictionary with result status
    """
    from ..data.loader import load_wetland_dataset
    from ..data.preprocessing import mask_region
    from ..data.config import get_region_bbox
    from ..analysis.trend import analyze_temporal_trends
    from ..visualization.maps import plot_trend_map

    try:
        # Load all years
        logger.info(f"Loading {dataset_name} for trend visualization ({start_year}-{end_year})")

        datasets = []
        for year in range(start_year, end_year + 1):
            try:
                ds = load_wetland_dataset(dataset_name, year=year)
                datasets.append(ds)
            except Exception as e:
                logger.warning(f"Could not load {dataset_name} for year {year}")

        if not datasets:
            return {
                'success': False,
                'error': f'Could not load any data for years {start_year}-{end_year}'
            }

        # Combine datasets
        import xarray as xr
        time_series = xr.concat(datasets, dim='time')

        # Apply region mask if specified
        if region:
            try:
                bbox = get_region_bbox(region)
                time_series = mask_region(time_series, bbox)
            except ValueError:
                logger.warning(f"Region '{region}' not found, ignoring")

        # Perform trend analysis
        trend_results = analyze_temporal_trends(time_series)

        # Create trend map
        title = f"Wetland Trend Analysis - {dataset_name} ({start_year}-{end_year})"

        fig = plot_trend_map(
            trend_results,
            variable='slope',
            title=title,
            save_path=output_path,
            show=False
        )

        import matplotlib.pyplot as plt
        plt.close(fig)

        return {
            'success': True,
            'dataset': dataset_name,
            'start_year': start_year,
            'end_year': end_year,
            'region': region,
            'output_path': output_path,
            'visualization_created': True
        }

    except Exception as e:
        logger.error(f"Error creating trend visualization: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def create_comparison_chart(
    dataset1_name: str,
    dataset2_name: str,
    output_path: str,
    year1: Optional[int] = None,
    year2: Optional[int] = None,
    chart_type: str = 'scatter',
    region: Optional[str] = None
) -> Dict:
    """
    Create a comparison chart between two datasets.

    Args:
        dataset1_name: Name of first dataset
        dataset2_name: Name of second dataset
        output_path: Path to save chart
        year1: Year for dataset1
        year2: Year for dataset2
        chart_type: Type of chart ('scatter', 'bar', 'box')
        region: Region to analyze

    Returns:
        Dictionary with result status
    """
    from ..data.loader import load_wetland_dataset
    from ..data.preprocessing import mask_region
    from ..data.config import get_region_bbox
    from ..visualization.charts import plot_comparison_scatter

    try:
        # Load datasets
        logger.info(f"Loading datasets for comparison chart: {dataset1_name} vs {dataset2_name}")
        ds1 = load_wetland_dataset(dataset1_name, year=year1)
        ds2 = load_wetland_dataset(dataset2_name, year=year2)

        # Apply region mask if specified
        if region:
            try:
                bbox = get_region_bbox(region)
                ds1 = mask_region(ds1, bbox)
                ds2 = mask_region(ds2, bbox)
            except ValueError:
                logger.warning(f"Region '{region}' not found, ignoring")

        # Flatten for scatter plot
        vals1 = ds1.values.ravel()
        vals2 = ds2.values.ravel()

        # Remove NaN
        valid_mask = ~__import__('numpy').isnan(vals1) & ~__import__('numpy').isnan(vals2)
        vals1 = vals1[valid_mask]
        vals2 = vals2[valid_mask]

        # Create chart
        title = f"Dataset Comparison: {dataset1_name} vs {dataset2_name}"
        labels = (dataset1_name, dataset2_name)

        if chart_type == 'scatter':
            fig = plot_comparison_scatter(
                vals1, vals2,
                labels=labels,
                title=title,
                save_path=output_path,
                show=False
            )
        else:
            return {
                'success': False,
                'error': f"Chart type '{chart_type}' not yet implemented"
            }

        import matplotlib.pyplot as plt
        plt.close(fig)

        return {
            'success': True,
            'dataset1': dataset1_name,
            'dataset2': dataset2_name,
            'year1': year1,
            'year2': year2,
            'region': region,
            'chart_type': chart_type,
            'output_path': output_path,
            'chart_created': True
        }

    except Exception as e:
        logger.error(f"Error creating comparison chart: {e}")
        return {
            'success': False,
            'error': str(e)
        }