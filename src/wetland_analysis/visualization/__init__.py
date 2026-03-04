"""
Visualization functions for wetland analysis results.
"""

from .maps import (
    plot_wetland_map,
    plot_trend_map,
    plot_comparison_map,
    create_animation
)
from .charts import (
    plot_accuracy_metrics,
    plot_trend_series,
    plot_comparison_scatter
)
from .reports import (
    generate_analysis_report,
    create_summary_figure
)

__all__ = [
    # Map plotting
    "plot_wetland_map",
    "plot_trend_map",
    "plot_comparison_map",
    "create_animation",

    # Chart plotting
    "plot_accuracy_metrics",
    "plot_trend_series",
    "plot_comparison_scatter",

    # Report generation
    "generate_analysis_report",
    "create_summary_figure",
]