"""
Report generation functions for wetland analysis.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_analysis_report(
    analysis_results: Dict[str, Any],
    output_format: str = 'markdown',
    include_plots: bool = True,
    plot_dir: Optional[str] = None
) -> str:
    """
    Generate analysis report from results.

    Parameters
    ----------
    analysis_results : dict
        Dictionary containing analysis results
    output_format : str, optional
        Output format: 'markdown', 'html', 'text'
    include_plots : bool, optional
        Whether to include plots in report
    plot_dir : str, optional
        Directory to save plots

    Returns
    -------
    str
        Generated report
    """
    # Initialize report sections
    sections = []

    # Title and timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sections.append(f"# Wetland Analysis Report\n\n*Generated: {timestamp}*\n")

    # Summary section
    if 'summary' in analysis_results:
        sections.append(_generate_summary_section(analysis_results['summary']))

    # Accuracy assessment section
    if 'accuracy' in analysis_results:
        sections.append(_generate_accuracy_section(analysis_results['accuracy']))

    # Trend analysis section
    if 'trend' in analysis_results:
        sections.append(_generate_trend_section(analysis_results['trend']))

    # Comparison section
    if 'comparison' in analysis_results:
        sections.append(_generate_comparison_section(analysis_results['comparison']))

    # Generate plots if requested
    if include_plots and plot_dir:
        plot_paths = _generate_report_plots(analysis_results, plot_dir)
        if plot_paths:
            sections.append(_generate_plots_section(plot_paths))

    # Conclusion
    sections.append(_generate_conclusion_section(analysis_results))

    # Combine sections
    report = '\n\n'.join(sections)

    # Convert to requested format
    if output_format == 'html':
        report = _markdown_to_html(report)
    elif output_format == 'text':
        report = _markdown_to_text(report)

    logger.info("Analysis report generated")
    return report


def _generate_summary_section(summary_results: Dict) -> str:
    """Generate summary section of report."""
    section = "## Summary\n\n"

    if 'n_valid_pixels' in summary_results:
        section += f"- **Valid Pixels**: {summary_results['n_valid_pixels']:,}\n"

    if 'dataset1_stats' in summary_results and 'dataset2_stats' in summary_results:
        ds1 = summary_results['dataset1_stats']
        ds2 = summary_results['dataset2_stats']

        section += "\n### Dataset Statistics\n\n"
        section += "| Statistic | Dataset 1 | Dataset 2 |\n"
        section += "|-----------|-----------|-----------|\n"
        section += f"| Mean | {ds1['mean']:.4f} | {ds2['mean']:.4f} |\n"
        section += f"| Std Dev | {ds1['std']:.4f} | {ds2['std']:.4f} |\n"
        section += f"| Min | {ds1['min']:.4f} | {ds2['min']:.4f} |\n"
        section += f"| Max | {ds1['max']:.4f} | {ds2['max']:.4f} |\n"

    return section


def _generate_accuracy_section(accuracy_results: Dict) -> str:
    """Generate accuracy assessment section."""
    section = "## Accuracy Assessment\n\n"

    # Overall metrics
    if 'overall_accuracy' in accuracy_results:
        oa = accuracy_results['overall_accuracy']
        kappa = accuracy_results.get('kappa', 'N/A')
        section += f"- **Overall Accuracy**: {oa:.3f}\n"
        section += f"- **Cohen's Kappa**: {kappa:.3f}\n"

    # Per-class metrics
    if 'per_class' in accuracy_results:
        section += "\n### Per-Class Metrics\n\n"
        section += "| Class | Producer's Acc | User's Acc | F1-Score | IoU |\n"
        section += "|-------|---------------|------------|----------|-----|\n"

        for class_name, metrics in accuracy_results['per_class'].items():
            pa = metrics.get('producer_accuracy', 0)
            ua = metrics.get('user_accuracy', 0)
            f1 = metrics.get('f1_score', 0)
            iou = metrics.get('iou', 0)
            section += f"| {class_name} | {pa:.3f} | {ua:.3f} | {f1:.3f} | {iou:.3f} |\n"

    # Confusion matrix (simplified)
    if 'confusion_matrix' in accuracy_results:
        cm = accuracy_results['confusion_matrix']
        if isinstance(cm, list) and len(cm) > 0:
            section += "\n### Confusion Matrix (Top 5x5)\n\n"
            cm_array = np.array(cm)
            # Show only first 5 classes if many
            n_show = min(5, cm_array.shape[0])
            for i in range(n_show):
                row = ' | '.join([str(int(x)) for x in cm_array[i, :n_show]])
                section += f"| {row} |\n"

    return section


def _generate_trend_section(trend_results: Dict) -> str:
    """Generate trend analysis section."""
    section = "## Trend Analysis\n\n"

    if 'trend' in trend_results:
        trend = trend_results['trend']
        p_value = trend_results.get('p_value', 1.0)
        significant = trend_results.get('significant', False)
        slope = trend_results.get('slope', np.nan)

        section += f"- **Trend Direction**: {trend}\n"
        section += f"- **Significant**: {significant} (p={p_value:.4f})\n"
        if not np.isnan(slope):
            section += f"- **Slope**: {slope:.6f} per time unit\n"

    if 'trend_distribution' in trend_results:
        dist = trend_results['trend_distribution']
        section += "\n### Trend Distribution\n\n"
        section += f"- **Increasing Trends**: {dist.get('increasing_percent', 0):.1f}%\n"
        section += f"- **Decreasing Trends**: {dist.get('decreasing_percent', 0):.1f}%\n"
        section += f"- **No Trend**: {dist.get('no_trend_percent', 0):.1f}%\n"

    if 'slope_statistics' in trend_results:
        stats = trend_results['slope_statistics']
        section += "\n### Slope Statistics\n\n"
        section += f"- **Mean Slope**: {stats.get('mean', 0):.6f}\n"
        section += f"- **Std Dev**: {stats.get('std', 0):.6f}\n"
        section += f"- **Min Slope**: {stats.get('min', 0):.6f}\n"
        section += f"- **Max Slope**: {stats.get('max', 0):.6f}\n"

    return section


def _generate_comparison_section(comparison_results: Dict) -> str:
    """Generate dataset comparison section."""
    section = "## Dataset Comparison\n\n"

    if 'correlation' in comparison_results:
        corr = comparison_results['correlation']
        section += "### Correlation\n\n"
        section += f"- **Pearson's r**: {corr.get('pearson_r', 'N/A'):.3f}\n"
        section += f"- **Spearman's ρ**: {corr.get('spearman_rho', 'N/A'):.3f}\n"
        section += f"- **R²**: {corr.get('r_squared', 'N/A'):.3f}\n"

    if 'bias' in comparison_results:
        bias = comparison_results['bias']
        section += "\n### Error Metrics\n\n"
        section += f"- **Mean Bias**: {bias.get('mean_bias', 'N/A'):.4f}\n"
        section += f"- **MAE**: {bias.get('mean_absolute_error', 'N/A'):.4f}\n"
        section += f"- **RMSE**: {bias.get('root_mean_square_error', 'N/A'):.4f}\n"

    if 'agreement' in comparison_results:
        agree = comparison_results['agreement']
        section += "\n### Agreement Metrics\n\n"
        section += f"- **Total Agreement**: {agree.get('total_agreement_percent', 'N/A'):.1f}%\n"
        section += f"- **Wetland Agreement**: {agree.get('wetland_agreement_pixels', 'N/A'):,} pixels\n"

    return section


def _generate_report_plots(
    analysis_results: Dict,
    plot_dir: str
) -> Dict[str, str]:
    """Generate plots for report and return file paths."""
    plot_paths = {}

    try:
        # Import plotting functions
        from .charts import (
            plot_accuracy_metrics,
            plot_confusion_matrix_heatmap,
            plot_comparison_scatter
        )
        from .maps import plot_trend_map

        # Create plot directory
        import os
        os.makedirs(plot_dir, exist_ok=True)

        # Generate accuracy plots
        if 'accuracy' in analysis_results:
            acc_plot_path = os.path.join(plot_dir, 'accuracy_metrics.png')
            try:
                fig = plot_accuracy_metrics(
                    analysis_results['accuracy'],
                    show=False,
                    save_path=acc_plot_path
                )
                plt.close(fig)
                plot_paths['accuracy'] = acc_plot_path
            except Exception as e:
                logger.error(f"Error generating accuracy plot: {e}")

        # Generate confusion matrix plot
        if 'accuracy' in analysis_results and 'confusion_matrix' in analysis_results['accuracy']:
            cm_plot_path = os.path.join(plot_dir, 'confusion_matrix.png')
            try:
                cm = np.array(analysis_results['accuracy']['confusion_matrix'])
                class_labels = analysis_results['accuracy'].get('class_labels')
                fig = plot_confusion_matrix_heatmap(
                    cm, class_labels=class_labels,
                    show=False, save_path=cm_plot_path
                )
                plt.close(fig)
                plot_paths['confusion_matrix'] = cm_plot_path
            except Exception as e:
                logger.error(f"Error generating confusion matrix plot: {e}")

        # Generate comparison scatter plot (if we have paired data)
        if 'summary' in analysis_results and 'dataset1_stats' in analysis_results['summary']:
            # This is a placeholder - actual data would be needed
            pass

    except Exception as e:
        logger.error(f"Error generating plots: {e}")

    return plot_paths


def _generate_plots_section(plot_paths: Dict[str, str]) -> str:
    """Generate section with plot references."""
    section = "## Visualizations\n\n"

    for plot_name, plot_path in plot_paths.items():
        # Convert plot name to readable format
        readable_name = plot_name.replace('_', ' ').title()
        # In Markdown, we reference the plot file
        section += f"### {readable_name}\n\n"
        section += f"![{readable_name}]({plot_path})\n\n"

    return section


def _generate_conclusion_section(analysis_results: Dict) -> str:
    """Generate conclusion section."""
    section = "## Conclusion\n\n"

    # Extract key findings
    key_findings = []

    # Accuracy conclusion
    if 'accuracy' in analysis_results:
        oa = analysis_results['accuracy'].get('overall_accuracy', 0)
        if oa >= 0.8:
            key_findings.append("High classification accuracy achieved")
        elif oa >= 0.6:
            key_findings.append("Moderate classification accuracy")
        else:
            key_findings.append("Low classification accuracy - needs improvement")

    # Trend conclusion
    if 'trend' in analysis_results:
        trend = analysis_results['trend'].get('trend', 'no_trend')
        if trend == 'increasing':
            key_findings.append("Overall increasing wetland trend detected")
        elif trend == 'decreasing':
            key_findings.append("Overall decreasing wetland trend detected")
        else:
            key_findings.append("No clear overall trend detected")

    # Comparison conclusion
    if 'correlation' in analysis_results.get('comparison', {}):
        corr = analysis_results['comparison']['correlation'].get('pearson_r', 0)
        if corr >= 0.7:
            key_findings.append("Strong correlation between datasets")
        elif corr >= 0.4:
            key_findings.append("Moderate correlation between datasets")
        else:
            key_findings.append("Weak correlation between datasets")

    # Generate conclusion text
    if key_findings:
        section += "### Key Findings\n\n"
        for finding in key_findings:
            section += f"- {finding}\n"

    section += "\n### Recommendations\n\n"
    section += "1. Validate results with ground truth data where available\n"
    section += "2. Consider seasonal variations in wetland dynamics\n"
    section += "3. Account for dataset-specific uncertainties and biases\n"
    section += "4. Use ensemble approaches for more robust estimates\n"

    return section


def _markdown_to_html(markdown_text: str) -> str:
    """Convert markdown to HTML (simple implementation)."""
    # This is a simple implementation - in production, use a proper markdown parser
    html = markdown_text.replace('\n\n', '</p><p>')
    html = html.replace('\n', '<br>')
    html = html.replace('### ', '<h3>').replace('\n', '</h3>')
    html = html.replace('## ', '<h2>').replace('\n', '</h2>')
    html = html.replace('# ', '<h1>').replace('\n', '</h1>')
    html = html.replace('**', '<strong>').replace('**', '</strong>')
    html = html.replace('*', '<em>').replace('*', '</em>')

    html = f"<html><body><p>{html}</p></body></html>"
    return html


def _markdown_to_text(markdown_text: str) -> str:
    """Convert markdown to plain text."""
    # Remove markdown formatting
    text = markdown_text
    text = text.replace('# ', '')
    text = text.replace('## ', '')
    text = text.replace('### ', '')
    text = text.replace('**', '')
    text = text.replace('*', '')
    text = text.replace('|', ' ')  # Remove table markers
    return text


def create_summary_figure(
    analysis_results: Dict[str, Any],
    figsize: Tuple[int, int] = (15, 10),
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Create summary figure with multiple subplots.

    Parameters
    ----------
    analysis_results : dict
        Analysis results
    figsize : tuple, optional
        Figure size (width, height)
    save_path : str, optional
        Path to save figure
    show : bool, optional
        Whether to display the figure

    Returns
    -------
    plt.Figure
        Matplotlib figure
    """
    # Determine what subplots to create
    n_subplots = 0
    has_accuracy = 'accuracy' in analysis_results
    has_trend = 'trend' in analysis_results
    has_comparison = 'comparison' in analysis_results

    if has_accuracy:
        n_subplots += 1
    if has_trend:
        n_subplots += 1
    if has_comparison:
        n_subplots += 1

    if n_subplots == 0:
        logger.warning("No analysis results to plot")
        return plt.figure()

    # Create figure with subplots
    n_cols = min(2, n_subplots)
    n_rows = (n_subplots + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    if n_subplots == 1:
        axes = np.array([axes])
    axes = axes.flatten()

    plot_idx = 0

    # Plot accuracy metrics
    if has_accuracy and plot_idx < len(axes):
        ax = axes[plot_idx]
        acc_results = analysis_results['accuracy']

        # Extract metrics
        metrics = []
        values = []

        if 'overall_accuracy' in acc_results:
            metrics.append('OA')
            values.append(acc_results['overall_accuracy'])

        if 'kappa' in acc_results:
            metrics.append('Kappa')
            values.append(acc_results['kappa'])

        # Plot bar chart
        if metrics:
            bars = ax.bar(metrics, values, color=['skyblue', 'lightgreen'])
            ax.set_ylim(0, 1)
            ax.set_ylabel('Score')
            ax.set_title('Accuracy Metrics', fontweight='bold')

            # Add value labels
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                       f'{value:.3f}', ha='center', fontsize=9)

            ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)

        plot_idx += 1

    # Plot trend information
    if has_trend and plot_idx < len(axes):
        ax = axes[plot_idx]
        trend_results = analysis_results['trend']

        # Create trend summary
        categories = ['Increasing', 'Decreasing', 'No Trend']
        if 'trend_distribution' in trend_results:
            dist = trend_results['trend_distribution']
            values = [
                dist.get('increasing_percent', 0),
                dist.get('decreasing_percent', 0),
                dist.get('no_trend_percent', 0)
            ]
        else:
            values = [0, 0, 100]

        # Plot pie chart or bar chart
        if sum(values) > 0:
            ax.pie(values, labels=categories, autopct='%1.1f%%',
                  colors=['lightcoral', 'lightblue', 'lightgray'])
            ax.set_title('Trend Distribution', fontweight='bold')

        plot_idx += 1

    # Plot comparison metrics
    if has_comparison and plot_idx < len(axes):
        ax = axes[plot_idx]
        comp_results = analysis_results['comparison']

        # Extract correlation and error metrics
        metrics_data = {}

        if 'correlation' in comp_results:
            metrics_data['Correlation'] = comp_results['correlation'].get('pearson_r', 0)

        if 'bias' in comp_results:
            metrics_data['RMSE'] = comp_results['bias'].get('root_mean_square_error', 0)
            metrics_data['Bias'] = comp_results['bias'].get('mean_bias', 0)

        if metrics_data:
            metrics = list(metrics_data.keys())
            values = list(metrics_data.values())

            bars = ax.bar(range(len(metrics)), values, color='steelblue', alpha=0.7)
            ax.set_xticks(range(len(metrics)))
            ax.set_xticklabels(metrics, rotation=45, ha='right')
            ax.set_title('Comparison Metrics', fontweight='bold')

            # Add value labels
            for i, (metric, value) in enumerate(zip(metrics, values)):
                ax.text(i, value + 0.01 * max(values), f'{value:.3f}',
                       ha='center', fontsize=9)

        plot_idx += 1

    # Hide unused subplots
    for j in range(plot_idx, len(axes)):
        axes[j].axis('off')

    # Main title
    fig.suptitle('Wetland Analysis Summary', fontsize=16, fontweight='bold', y=0.95)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Summary figure saved to {save_path}")

    if show:
        plt.show()
    else:
        plt.close()

    return fig