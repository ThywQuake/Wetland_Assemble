"""
Analysis functions for wetland dataset evaluation.
"""

from .accuracy import (
    calculate_spatial_accuracy,
    calculate_confusion_matrix,
    calculate_classification_metrics
)
from .trend import (
    calculate_mann_kendall_trend,
    calculate_sens_slope,
    analyze_temporal_trends
)
from .comparison import (
    compare_datasets,
    calculate_agreement_metrics,
    analyze_spatial_patterns
)

__all__ = [
    # Accuracy assessment
    "calculate_spatial_accuracy",
    "calculate_confusion_matrix",
    "calculate_classification_metrics",

    # Trend analysis
    "calculate_mann_kendall_trend",
    "calculate_sens_slope",
    "analyze_temporal_trends",

    # Dataset comparison
    "compare_datasets",
    "calculate_agreement_metrics",
    "analyze_spatial_patterns",
]