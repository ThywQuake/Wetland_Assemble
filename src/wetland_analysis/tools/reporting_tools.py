"""
Reporting tools for AI agents.
"""

from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


def generate_report(
    output_path: str,
    analysis_type: str = 'all',
    dataset_name: Optional[str] = None,
    include_plots: bool = True
) -> Dict:
    """
    Generate an analysis report.

    Args:
        output_path: Path to save the report
        analysis_type: Type of analysis ('accuracy', 'trend', 'comparison', 'all')
        dataset_name: Dataset name for the report
        include_plots: Whether to include plots

    Returns:
        Dictionary with result status
    """
    from ..visualization.reports import generate_analysis_report

    try:
        # Create empty analysis results for report structure
        analysis_results = {
            'analysis_type': analysis_type,
            'dataset': dataset_name
        }

        # Generate report
        report = generate_analysis_report(
            analysis_results,
            output_format='markdown',
            include_plots=include_plots
        )

        # Save report
        with open(output_path, 'w') as f:
            f.write(report)

        return {
            'success': True,
            'output_path': output_path,
            'analysis_type': analysis_type,
            'report_created': True
        }

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def export_results(
    results: Dict,
    output_path: str,
    format: str = 'json'
) -> Dict:
    """
    Export analysis results to a file.

    Args:
        results: Results dictionary to export
        output_path: Path to save results
        format: Output format ('json', 'yaml', 'pickle')

    Returns:
        Dictionary with result status
    """
    from ..utils.file_io import save_results

    try:
        save_results(results, output_path, format=format)

        return {
            'success': True,
            'output_path': output_path,
            'format': format,
            'results_exported': True
        }

    except Exception as e:
        logger.error(f"Error exporting results: {e}")
        return {
            'success': False,
            'error': str(e)
        }