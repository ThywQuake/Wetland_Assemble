"""
Analysis tools for AI agents.
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def compare_datasets(
    dataset1_name: str,
    dataset2_name: str,
    year1: Optional[int] = None,
    year2: Optional[int] = None,
    metrics: Optional[List[str]] = None,
    region: Optional[str] = None
) -> Dict:
    """
    Compare two wetland datasets.

    Args:
        dataset1_name: Name of first dataset
        dataset2_name: Name of second dataset
        year1: Year for dataset1
        year2: Year for dataset2
        metrics: Metrics to calculate
        region: Region to analyze

    Returns:
        Dictionary with comparison results
    """
    from ..data.loader import load_wetland_dataset
    from ..data.preprocessing import mask_region
    from ..data.config import get_region_bbox
    from ..analysis.comparison import compare_datasets as _compare

    try:
        if metrics is None:
            metrics = ['accuracy', 'agreement', 'correlation', 'bias']

        # Load datasets
        logger.info(f"Loading datasets for comparison: {dataset1_name} vs {dataset2_name}")
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

        # Perform comparison
        results = _compare(ds1, ds2, metrics=metrics)

        # Simplify results for agent consumption
        summary = {
            'dataset1': dataset1_name,
            'dataset2': dataset2_name,
            'year1': year1,
            'year2': year2,
            'region': region,
            'metrics': metrics,
            'results': results
        }

        return {
            'success': True,
            'comparison': summary
        }

    except Exception as e:
        logger.error(f"Error comparing datasets: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def analyze_trends(
    dataset_name: str,
    start_year: int,
    end_year: int,
    region: Optional[str] = None,
    alpha: float = 0.05
) -> Dict:
    """
    Analyze temporal trends in a wetland dataset.

    Args:
        dataset_name: Name of dataset to analyze
        start_year: Start year for analysis
        end_year: End year for analysis
        region: Region to analyze
        alpha: Significance level

    Returns:
        Dictionary with trend analysis results
    """
    from ..data.loader import load_wetland_dataset
    from ..data.preprocessing import mask_region
    from ..data.config import get_region_bbox
    from ..analysis.trend import analyze_temporal_trends, calculate_trend_metrics

    try:
        # Load all years
        logger.info(f"Loading {dataset_name} for trend analysis ({start_year}-{end_year})")

        # Try to load multi-year dataset
        datasets = []
        for year in range(start_year, end_year + 1):
            try:
                ds = load_wetland_dataset(dataset_name, year=year)
                datasets.append(ds)
            except Exception as e:
                logger.warning(f"Could not load {dataset_name} for year {year}: {e}")

        if not datasets:
            return {
                'success': False,
                'error': f'Could not load any data for years {start_year}-{end_year}'
            }

        # Combine datasets along time dimension
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
        logger.info("Performing trend analysis...")
        trend_results = analyze_temporal_trends(time_series, alpha=alpha)

        # Calculate summary metrics
        summary = calculate_trend_metrics(trend_results)

        return {
            'success': True,
            'dataset': dataset_name,
            'start_year': start_year,
            'end_year': end_year,
            'region': region,
            'alpha': alpha,
            'trend_summary': summary,
            'trend_results_available': True
        }

    except Exception as e:
        logger.error(f"Error analyzing trends: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def calculate_accuracy(
    reference_dataset: str,
    target_dataset: str,
    year_ref: Optional[int] = None,
    year_tgt: Optional[int] = None,
    metrics: Optional[List[str]] = None,
    region: Optional[str] = None
) -> Dict:
    """
    Calculate classification accuracy metrics.

    Args:
        reference_dataset: Reference (ground truth) dataset name
        target_dataset: Target (predicted) dataset name
        year_ref: Year for reference dataset
        year_tgt: Year for target dataset
        metrics: Metrics to calculate
        region: Region to analyze

    Returns:
        Dictionary with accuracy metrics
    """
    from ..data.loader import load_wetland_dataset
    from ..data.preprocessing import mask_region
    from ..data.config import get_region_bbox
    from ..analysis.accuracy import calculate_spatial_accuracy

    try:
        if metrics is None:
            metrics = ['OA', 'Kappa', 'PA', 'UA', 'F1', 'IoU']

        # Load datasets
        logger.info(f"Loading datasets for accuracy: {reference_dataset} vs {target_dataset}")
        ref_data = load_wetland_dataset(reference_dataset, year=year_ref)
        tgt_data = load_wetland_dataset(target_dataset, year=year_tgt)

        # Apply region mask if specified
        if region:
            try:
                bbox = get_region_bbox(region)
                ref_data = mask_region(ref_data, bbox)
                tgt_data = mask_region(tgt_data, bbox)
            except ValueError:
                logger.warning(f"Region '{region}' not found, ignoring")

        # Calculate accuracy
        results = calculate_spatial_accuracy(ref_data, tgt_data, metrics=metrics)

        return {
            'success': True,
            'reference': reference_dataset,
            'target': target_dataset,
            'year_reference': year_ref,
            'year_target': year_tgt,
            'region': region,
            'metrics': metrics,
            'accuracy_results': results
        }

    except Exception as e:
        logger.error(f"Error calculating accuracy: {e}")
        return {
            'success': False,
            'error': str(e)
        }