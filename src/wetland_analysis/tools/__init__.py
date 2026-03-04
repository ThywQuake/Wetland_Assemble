"""
Agent tool interfaces for wetland analysis.

This module provides AI-agent accessible tools for wetland dataset analysis.
Each tool function is designed to be callable by AI agents with structured inputs and outputs.
"""

from .loader_tools import (
    list_datasets,
    get_dataset_info,
    load_dataset
)
from .analysis_tools import (
    compare_datasets,
    analyze_trends,
    calculate_accuracy
)
from .visualization_tools import (
    create_map,
    create_trend_visualization,
    create_comparison_chart
)
from .reporting_tools import (
    generate_report,
    export_results
)

__all__ = [
    # Data loading tools
    "list_datasets",
    "get_dataset_info",
    "load_dataset",

    # Analysis tools
    "compare_datasets",
    "analyze_trends",
    "calculate_accuracy",

    # Visualization tools
    "create_map",
    "create_trend_visualization",
    "create_comparison_chart",

    # Reporting tools
    "generate_report",
    "export_results",

    # Tool registry
    "get_tool_definitions",
    "get_system_prompt"
]


def get_tool_definitions() -> list:
    """
    Get all tool definitions for AI agents.

    Returns:
        List of tool definitions in OpenAI/Claude function calling format
    """
    from .loader_tools import list_datasets, get_dataset_info, load_dataset
    from .analysis_tools import compare_datasets, analyze_trends, calculate_accuracy
    from .visualization_tools import create_map, create_trend_visualization, create_comparison_chart
    from .reporting_tools import generate_report, export_results

    tools = [
        # Data loading tools
        {
            "type": "function",
            "function": {
                "name": "list_datasets",
                "description": "List all available wetland datasets that can be loaded for analysis.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_dataset_info",
                "description": "Get detailed information about a specific wetland dataset including its format, resolution, time range, and variables.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset (e.g., 'gwd30', 'giems_mc', 'glwd_v2', 'g2017', 'wad2m', 'swamps', 'lstm_wetland', 'berkeley_rwawc')"
                        }
                    },
                    "required": ["dataset_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "load_dataset",
                "description": "Load a wetland dataset for analysis. Returns xarray data that can be used for further processing.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to load"
                        },
                        "year": {
                            "type": "integer",
                            "description": "Year for annual/monthly datasets (optional)"
                        },
                        "month": {
                            "type": "integer",
                            "description": "Month for monthly datasets (optional, 1-12)"
                        },
                        "region": {
                            "type": "string",
                            "description": "Region to clip data to (optional): 'tropical', 'subtropical', 'tropical_subtropical', 'global'"
                        }
                    },
                    "required": ["dataset_name"]
                }
            }
        },

        # Analysis tools
        {
            "type": "function",
            "function": {
                "name": "compare_datasets",
                "description": "Compare two wetland datasets and calculate agreement, correlation, and bias metrics.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dataset1_name": {
                            "type": "string",
                            "description": "Name of the first dataset"
                        },
                        "dataset2_name": {
                            "type": "string",
                            "description": "Name of the second dataset"
                        },
                        "year1": {
                            "type": "integer",
                            "description": "Year for dataset1 (optional)"
                        },
                        "year2": {
                            "type": "integer",
                            "description": "Year for dataset2 (optional)"
                        },
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Metrics to calculate: 'accuracy', 'agreement', 'correlation', 'bias'",
                            "default": ["accuracy", "agreement", "correlation"]
                        },
                        "region": {
                            "type": "string",
                            "description": "Region to analyze (optional)"
                        }
                    },
                    "required": ["dataset1_name", "dataset2_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_trends",
                "description": "Analyze temporal trends in a wetland dataset using Mann-Kendall test and Sen's slope.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to analyze"
                        },
                        "start_year": {
                            "type": "integer",
                            "description": "Start year for trend analysis"
                        },
                        "end_year": {
                            "type": "integer",
                            "description": "End year for trend analysis"
                        },
                        "region": {
                            "type": "string",
                            "description": "Region to analyze (optional)"
                        },
                        "alpha": {
                            "type": "number",
                            "description": "Significance level for trend test (default 0.05)",
                            "default": 0.05
                        }
                    },
                    "required": ["dataset_name", "start_year", "end_year"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_accuracy",
                "description": "Calculate classification accuracy metrics (OA, Kappa, IoU, etc.) between reference and target datasets.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reference_dataset": {
                            "type": "string",
                            "description": "Name of reference (ground truth) dataset"
                        },
                        "target_dataset": {
                            "type": "string",
                            "description": "Name of target (predicted) dataset"
                        },
                        "year_ref": {
                            "type": "integer",
                            "description": "Year for reference dataset (optional)"
                        },
                        "year_tgt": {
                            "type": "integer",
                            "description": "Year for target dataset (optional)"
                        },
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Metrics to calculate: 'OA', 'Kappa', 'PA', 'UA', 'F1', 'IoU'",
                            "default": ["OA", "Kappa", "IoU"]
                        },
                        "region": {
                            "type": "string",
                            "description": "Region to analyze (optional)"
                        }
                    },
                    "required": ["reference_dataset", "target_dataset"]
                }
            }
        },

        # Visualization tools
        {
            "type": "function",
            "function": {
                "name": "create_map",
                "description": "Create a wetland distribution map.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to visualize"
                        },
                        "year": {
                            "type": "integer",
                            "description": "Year for the visualization"
                        },
                        "title": {
                            "type": "string",
                            "description": "Title for the map (optional)",
                            "default": "Wetland Distribution"
                        },
                        "output_path": {
                            "type": "string",
                            "description": "Path to save the map image"
                        },
                        "region": {
                            "type": "string",
                            "description": "Region to visualize (optional)"
                        }
                    },
                    "required": ["dataset_name", "year", "output_path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_trend_visualization",
                "description": "Create a visualization of temporal trends in wetland data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to visualize"
                        },
                        "start_year": {
                            "type": "integer",
                            "description": "Start year for visualization"
                        },
                        "end_year": {
                            "type": "integer",
                            "description": "End year for visualization"
                        },
                        "output_path": {
                            "type": "string",
                            "description": "Path to save the visualization"
                        },
                        "region": {
                            "type": "string",
                            "description": "Region to visualize (optional)"
                        }
                    },
                    "required": ["dataset_name", "start_year", "end_year", "output_path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_comparison_chart",
                "description": "Create a comparison chart between two datasets.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dataset1_name": {
                            "type": "string",
                            "description": "Name of the first dataset"
                        },
                        "dataset2_name": {
                            "type": "string",
                            "description": "Name of the second dataset"
                        },
                        "year1": {
                            "type": "integer",
                            "description": "Year for dataset1 (optional)"
                        },
                        "year2": {
                            "type": "integer",
                            "description": "Year for dataset2 (optional)"
                        },
                        "chart_type": {
                            "type": "string",
                            "description": "Type of chart: 'scatter', 'bar', 'box'",
                            "default": "scatter"
                        },
                        "output_path": {
                            "type": "string",
                            "description": "Path to save the chart"
                        },
                        "region": {
                            "type": "string",
                            "description": "Region to analyze (optional)"
                        }
                    },
                    "required": ["dataset1_name", "dataset2_name", "output_path"]
                }
            }
        },

        # Reporting tools
        {
            "type": "function",
            "function": {
                "name": "generate_report",
                "description": "Generate a comprehensive analysis report in Markdown format.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "analysis_type": {
                            "type": "string",
                            "description": "Type of analysis: 'accuracy', 'trend', 'comparison', 'all'",
                            "default": "all"
                        },
                        "dataset_name": {
                            "type": "string",
                            "description": "Dataset name for the report (optional)"
                        },
                        "output_path": {
                            "type": "string",
                            "description": "Path to save the report"
                        },
                        "include_plots": {
                            "type": "boolean",
                            "description": "Whether to include plots in the report",
                            "default": True
                        }
                    },
                    "required": ["output_path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "export_results",
                "description": "Export analysis results to a file in various formats.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "object",
                            "description": "Results dictionary to export"
                        },
                        "output_path": {
                            "type": "string",
                            "description": "Path to save the results"
                        },
                        "format": {
                            "type": "string",
                            "description": "Output format: 'json', 'yaml', 'pickle'",
                            "default": "json"
                        }
                    },
                    "required": ["results", "output_path"]
                }
            }
        }
    ]

    return tools


def get_system_prompt() -> str:
    """
    Get the system prompt for AI agents working with wetland analysis.

    Returns:
        System prompt string
    """
    return """You are an expert AI assistant for wetland dataset analysis. You have access to a comprehensive set of tools for analyzing satellite-derived wetland datasets.

## Available Capabilities

### Data Loading
- **list_datasets**: List all available wetland datasets
- **get_dataset_info**: Get detailed information about a specific dataset
- **load_dataset**: Load a dataset for analysis

Available datasets:
- gwd30: Global Wetland Dataset 30m (annual, 2013-2022)
- giems_mc: GIEMS-MC Monthly Inundation (1993-2007)
- glwd_v2: Global Lakes and Wetlands Database v2 (static)
- g2017: Global 2017 Wetland and Peatland Dataset (tropical/subtropical)
- wad2m: Wetland Area and Dynamics for Methane Modeling (monthly, 2000-2020)
- swamps: Surface Water Microwave Product Series (daily, 1992-2020)
- lstm_wetland: LSTM-based Wetland Prediction
- berkeley_rwawc: UC Berkeley Remote Sensing of Water Mask (monthly, 2018-2019)

### Analysis
- **compare_datasets**: Compare two datasets (agreement, correlation, bias)
- **analyze_trends**: Perform Mann-Kendall trend analysis
- **calculate_accuracy**: Calculate classification accuracy metrics

### Visualization
- **create_map**: Generate wetland distribution maps
- **create_trend_visualization**: Create trend visualization charts
- **create_comparison_chart**: Create comparison charts

### Reporting
- **generate_report**: Generate analysis reports
- **export_results**: Export results to files

## Typical Workflows

### Cross-Dataset Comparison
1. Use list_datasets to see available datasets
2. Use get_dataset_info to understand dataset characteristics
3. Use compare_datasets to compare two datasets
4. Use create_comparison_chart to visualize differences
5. Use generate_report to create a summary report

### Trend Analysis
1. Load a time-series dataset with load_dataset
2. Use analyze_trends to detect temporal changes
3. Use create_trend_visualization to visualize trends
4. Use export_results to save trend metrics

### Accuracy Assessment
1. Load reference and target datasets
2. Use calculate_accuracy to compute OA, Kappa, IoU, etc.
3. Use create_map to visualize spatial accuracy patterns
4. Use generate_report to document accuracy results

## Key Concepts

- **OA (Overall Accuracy)**: Proportion of correctly classified pixels
- **Kappa**: Cohen's Kappa coefficient for agreement
- **IoU (Intersection over Union)**: Spatial overlap measure
- **Mann-Kendall Test**: Non-parametric trend detection
- **Sen's Slope**: Robust slope estimator for trends

## Guidelines

1. Always check dataset availability with list_datasets first
2. Use get_dataset_info to understand dataset format before loading
3. For comparisons, ensure datasets cover the same time period and region
4. Set appropriate alpha values for statistical tests (default 0.05)
5. Use region parameters to focus analysis on areas of interest
6. Export results regularly to avoid data loss

You can help users perform sophisticated wetland dataset analyses by combining these tools in logical sequences."""