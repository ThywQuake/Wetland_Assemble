"""
Chart visualization functions for wetland analysis.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)


def plot_accuracy_metrics(
    accuracy_results: Dict,
    metrics: List[str] = None,
    figsize: Tuple[int, int] = (12, 8),
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot accuracy assessment metrics.

    Parameters
    ----------
    accuracy_results : dict
        Accuracy metrics from calculate_spatial_accuracy
    metrics : list of str, optional
        Metrics to plot. Default: ['OA', 'Kappa', 'PA', 'UA', 'F1', 'IoU']
    figsize : tuple, optional
        Figure size (width, height)
    save_path : str, optional
        Path to save figure
    show : bool, optional
        Whether to display the figure

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    """
    if metrics is None:
        metrics = ['OA', 'Kappa', 'PA', 'UA', 'F1', 'IoU']

    # Create figure with subplots
    n_metrics = len(metrics)
    n_cols = min(3, n_metrics)
    n_rows = (n_metrics + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    if n_metrics == 1:
        axes = np.array([axes])
    axes = axes.flatten()

    # Plot each metric
    for i, metric in enumerate(metrics):
        ax = axes[i]
        metric_lower = metric.lower()

        if metric_lower == 'oa':
            # Overall Accuracy
            oa = accuracy_results.get('overall_accuracy', 0)
            ax.bar(['OA'], [oa], color='skyblue')
            ax.set_ylim(0, 1)
            ax.set_ylabel('Accuracy')
            ax.set_title(f'Overall Accuracy: {oa:.3f}')
            ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)

        elif metric_lower == 'kappa':
            # Cohen's Kappa
            kappa = accuracy_results.get('kappa', 0)
            ax.bar(['Kappa'], [kappa], color='lightgreen')
            ax.set_ylim(-1, 1)
            ax.set_ylabel('Kappa')
            ax.set_title(f"Cohen's Kappa: {kappa:.3f}")
            ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)

        elif metric_lower in ['pa', 'ua', 'f1', 'iou']:
            # Per-class metrics
            metric_name = {
                'pa': 'producer_accuracy',
                'ua': 'user_accuracy',
                'f1': 'f1_score',
                'iou': 'iou'
            }[metric_lower]

            display_name = {
                'pa': "Producer's Accuracy",
                'ua': "User's Accuracy",
                'f1': 'F1-Score',
                'iou': 'IoU'
            }[metric_lower]

            if metric_name in accuracy_results:
                class_metrics = accuracy_results[metric_name]
                classes = list(class_metrics.keys())
                values = list(class_metrics.values())

                ax.bar(range(len(classes)), values, color='lightcoral')
                ax.set_xticks(range(len(classes)))
                ax.set_xticklabels(classes, rotation=45, ha='right')
                ax.set_ylim(0, 1)
                ax.set_ylabel(display_name)
                ax.set_title(f'{display_name} by Class')

                # Add value labels on bars
                for j, v in enumerate(values):
                    ax.text(j, v + 0.02, f'{v:.2f}', ha='center', fontsize=8)
            else:
                ax.text(0.5, 0.5, f'{metric} not available',
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_title(display_name)

        else:
            ax.text(0.5, 0.5, f'Metric {metric} not implemented',
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title(metric)

    # Hide unused subplots
    for j in range(i + 1, len(axes)):
        axes[j].axis('off')

    plt.suptitle('Accuracy Assessment Metrics', fontsize=14, fontweight='bold')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Accuracy metrics plot saved to {save_path}")

    if show:
        plt.show()
    else:
        plt.close()

    return fig


def plot_trend_series(
    time_series: Union[np.ndarray, pd.Series, List],
    time_labels: Optional[List] = None,
    trend_line: bool = True,
    confidence_interval: bool = True,
    title: str = "Time Series Trend",
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot time series with trend analysis.

    Parameters
    ----------
    time_series : array-like
        Time series data
    time_labels : list, optional
        Labels for time points
    trend_line : bool, optional
        Whether to plot trend line
    confidence_interval : bool, optional
        Whether to plot confidence interval
    title : str, optional
        Plot title
    figsize : tuple, optional
        Figure size (width, height)
    save_path : str, optional
        Path to save figure
    show : bool, optional
        Whether to display the figure

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    """
    # Convert to numpy array
    y = np.asarray(time_series)

    # Create time index
    if time_labels is None:
        x = np.arange(len(y))
        x_labels = x
    else:
        x = np.arange(len(time_labels))
        x_labels = time_labels

    # Remove NaN values
    valid_mask = ~np.isnan(y)
    x_valid = x[valid_mask]
    y_valid = y[valid_mask]

    if len(y_valid) < 2:
        logger.error("Not enough valid data points for trend plot")
        return plt.figure()

    fig, ax = plt.subplots(figsize=figsize)

    # Plot time series
    ax.plot(x_valid, y_valid, 'bo-', linewidth=2, markersize=6,
           label='Observed', alpha=0.7)

    if trend_line:
        # Calculate linear trend
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_valid, y_valid)

        # Plot trend line
        trend_y = intercept + slope * x_valid
        ax.plot(x_valid, trend_y, 'r--', linewidth=2, label=f'Trend (slope={slope:.4f})')

        if confidence_interval:
            # Calculate confidence interval
            n = len(x_valid)
            t_critical = stats.t.ppf(0.975, n - 2)  # 95% confidence
            ci = t_critical * std_err * np.sqrt(1/n + (x_valid - np.mean(x_valid))**2 / np.sum((x_valid - np.mean(x_valid))**2))

            # Plot confidence interval
            ax.fill_between(x_valid, trend_y - ci, trend_y + ci,
                           color='red', alpha=0.2, label='95% CI')

        # Add trend statistics to title
        title += f' (slope={slope:.4f}, p={p_value:.4f})'

    # Formatting
    ax.set_xlabel('Time')
    ax.set_ylabel('Value')
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Set x-axis labels if provided
    if time_labels is not None:
        ax.set_xticks(x[::max(1, len(x)//10)])  # Show ~10 labels
        ax.set_xticklabels([str(label) for label in x_labels[::max(1, len(x)//10)]],
                          rotation=45, ha='right')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Trend series plot saved to {save_path}")

    if show:
        plt.show()
    else:
        plt.close()

    return fig


def plot_comparison_scatter(
    dataset1: Union[np.ndarray, List],
    dataset2: Union[np.ndarray, List],
    labels: Tuple[str, str] = ('Dataset 1', 'Dataset 2'),
    regression_line: bool = True,
    one_to_one_line: bool = True,
    title: str = "Dataset Comparison",
    figsize: Tuple[int, int] = (8, 8),
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot scatter plot comparing two datasets.

    Parameters
    ----------
    dataset1, dataset2 : array-like
        Datasets to compare
    labels : tuple, optional
        Labels for datasets
    regression_line : bool, optional
        Whether to plot regression line
    one_to_one_line : bool, optional
        Whether to plot 1:1 line
    title : str, optional
        Plot title
    figsize : tuple, optional
        Figure size (width, height)
    save_path : str, optional
        Path to save figure
    show : bool, optional
        Whether to display the figure

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    """
    # Convert to numpy arrays
    x = np.asarray(dataset1).ravel()
    y = np.asarray(dataset2).ravel()

    # Remove NaN values
    valid_mask = ~np.isnan(x) & ~np.isnan(y)
    x_valid = x[valid_mask]
    y_valid = y[valid_mask]

    if len(x_valid) < 2:
        logger.error("Not enough valid data points for scatter plot")
        return plt.figure()

    fig, ax = plt.subplots(figsize=figsize)

    # Create scatter plot
    scatter = ax.scatter(x_valid, y_valid, alpha=0.5, s=20, edgecolors='none')

    # Calculate statistics
    correlation = np.corrcoef(x_valid, y_valid)[0, 1]
    rmse = np.sqrt(np.mean((x_valid - y_valid) ** 2))
    bias = np.mean(y_valid - x_valid)

    # Plot 1:1 line
    if one_to_one_line:
        lims = [np.min([ax.get_xlim(), ax.get_ylim()]),
                np.max([ax.get_xlim(), ax.get_ylim()])]
        ax.plot(lims, lims, 'k--', alpha=0.5, linewidth=1, label='1:1 line')

    # Plot regression line
    if regression_line:
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_valid, y_valid)

        x_range = np.array([x_valid.min(), x_valid.max()])
        y_pred = intercept + slope * x_range
        ax.plot(x_range, y_pred, 'r-', linewidth=2,
               label=f'Regression (r={correlation:.3f})')

    # Set labels and title
    ax.set_xlabel(labels[0])
    ax.set_ylabel(labels[1])
    ax.set_title(f'{title}\nCorrelation: {correlation:.3f}, RMSE: {rmse:.3f}, Bias: {bias:.3f}',
                fontsize=12, fontweight='bold')

    # Add legend
    ax.legend()

    # Add grid
    ax.grid(True, alpha=0.3)

    # Set equal aspect ratio
    ax.set_aspect('equal', adjustable='box')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Comparison scatter plot saved to {save_path}")

    if show:
        plt.show()
    else:
        plt.close()

    return fig


def plot_confusion_matrix_heatmap(
    confusion_mat: np.ndarray,
    class_labels: Optional[List[str]] = None,
    normalize: bool = True,
    title: str = "Confusion Matrix",
    figsize: Tuple[int, int] = (8, 6),
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot confusion matrix as heatmap.

    Parameters
    ----------
    confusion_mat : np.ndarray
        Confusion matrix (n_classes x n_classes)
    class_labels : list of str, optional
        Labels for classes
    normalize : bool, optional
        Whether to normalize by row (true class)
    title : str, optional
        Plot title
    figsize : tuple, optional
        Figure size (width, height)
    save_path : str, optional
        Path to save figure
    show : bool, optional
        Whether to display the figure

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    """
    # Normalize if requested
    if normalize:
        cm = confusion_mat.astype('float') / confusion_mat.sum(axis=1)[:, np.newaxis]
        fmt = '.2f'
        label = 'Normalized by True Class'
    else:
        cm = confusion_mat
        fmt = 'd'
        label = 'Count'

    # Create labels if not provided
    n_classes = cm.shape[0]
    if class_labels is None:
        class_labels = [f'Class {i}' for i in range(n_classes)]

    fig, ax = plt.subplots(figsize=figsize)

    # Create heatmap
    im = ax.imshow(cm, interpolation='nearest', cmap='Blues')
    ax.figure.colorbar(im, ax=ax, label=label)

    # Set ticks and labels
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           xticklabels=class_labels,
           yticklabels=class_labels,
           title=title,
           ylabel='True Class',
           xlabel='Predicted Class')

    # Rotate tick labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Add text annotations
    thresh = cm.max() / 2. if normalize else cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            text = f'{cm[i, j]:{fmt}}'
            if normalize:
                text = f'{cm[i, j]:.2f}'  # Force 2 decimal places for normalized
            ax.text(j, i, text,
                   ha="center", va="center",
                   color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Confusion matrix heatmap saved to {save_path}")

    if show:
        plt.show()
    else:
        plt.close()

    return fig


def plot_metric_comparison(
    metric_dict: Dict[str, Dict],
    metric_name: str = 'overall_accuracy',
    title: str = "Metric Comparison",
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot comparison of a metric across multiple datasets or methods.

    Parameters
    ----------
    metric_dict : dict
        Dictionary with dataset/method names as keys and metric dictionaries as values
    metric_name : str, optional
        Name of metric to compare
    title : str, optional
        Plot title
    figsize : tuple, optional
        Figure size (width, height)
    save_path : str, optional
        Path to save figure
    show : bool, optional
        Whether to display the figure

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    """
    # Extract metric values
    names = []
    values = []

    for name, metrics in metric_dict.items():
        # Handle nested metric dictionaries
        if metric_name in metrics:
            value = metrics[metric_name]
        elif 'per_class' in metrics and metric_name in metrics['per_class']:
            value = metrics['per_class'][metric_name]
        else:
            # Try to find metric in nested structure
            value = None
            for k, v in metrics.items():
                if isinstance(v, dict) and metric_name in v:
                    value = v[metric_name]
                    break

        if value is not None:
            # Handle both scalar and dictionary values
            if isinstance(value, dict):
                # Take mean of per-class values
                value = np.mean(list(value.values()))
            names.append(name)
            values.append(float(value))

    if not values:
        logger.error(f"Metric '{metric_name}' not found in any dataset")
        return plt.figure()

    fig, ax = plt.subplots(figsize=figsize)

    # Create bar plot
    x_pos = np.arange(len(names))
    bars = ax.bar(x_pos, values, color='steelblue', alpha=0.7)

    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
               f'{value:.3f}', ha='center', va='bottom', fontsize=9)

    # Formatting
    ax.set_xlabel('Dataset/Method')
    ax.set_ylabel(metric_name.replace('_', ' ').title())
    ax.set_title(f'{title} - {metric_name.replace("_", " ").title()}', fontsize=12, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(names, rotation=45, ha='right')
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Metric comparison plot saved to {save_path}")

    if show:
        plt.show()
    else:
        plt.close()

    return fig