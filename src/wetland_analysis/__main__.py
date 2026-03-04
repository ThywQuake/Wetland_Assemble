"""
Main entry point for wetland analysis package.
"""

import argparse
import sys
from pathlib import Path

from .utils.logging import setup_logging


def main():
    """Main entry point for command-line interface."""
    parser = argparse.ArgumentParser(
        description="Wetland dataset classification accuracy evaluation and trend analysis"
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )

    parser.add_argument(
        "--dataset1",
        type=str,
        help="First dataset name or path"
    )

    parser.add_argument(
        "--dataset2",
        type=str,
        help="Second dataset name or path"
    )

    parser.add_argument(
        "--analysis",
        type=str,
        choices=["accuracy", "trend", "comparison", "all"],
        default="all",
        help="Type of analysis to perform"
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Output directory for results"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )

    parser.add_argument(
        "--log-file",
        type=str,
        help="Log file path"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="wetland-analysis 0.1.0"
    )

    args = parser.parse_args()

    # Setup logging
    log_level = getattr(logging, args.log_level)
    setup_logging(level=log_level, log_file=args.log_file)

    # Import here to avoid loading heavy dependencies during CLI parsing
    from .data.loader import load_wetland_dataset
    from .analysis.accuracy import calculate_spatial_accuracy
    from .analysis.trend import analyze_temporal_trends
    from .analysis.comparison import compare_datasets
    from .utils.file_io import save_results

    print("Wetland Analysis Tool")
    print("=" * 50)

    # Check if we have enough arguments
    if not args.dataset1:
        print("Error: At least one dataset is required")
        parser.print_help()
        sys.exit(1)

    try:
        # Load datasets
        print(f"Loading dataset: {args.dataset1}")
        dataset1 = load_wetland_dataset(args.dataset1)

        if args.dataset2:
            print(f"Loading dataset: {args.dataset2}")
            dataset2 = load_wetland_dataset(args.dataset2)

        results = {}

        # Perform analysis
        if args.analysis in ["accuracy", "all"] and args.dataset2:
            print("Performing accuracy assessment...")
            accuracy_results = calculate_spatial_accuracy(dataset1, dataset2)
            results["accuracy"] = accuracy_results
            print(f"Overall Accuracy: {accuracy_results.get('overall_accuracy', 'N/A'):.3f}")

        if args.analysis in ["trend", "all"] and "time" in dataset1.dims:
            print("Performing trend analysis...")
            trend_results = analyze_temporal_trends(dataset1)
            results["trend"] = trend_results
            print("Trend analysis completed")

        if args.analysis in ["comparison", "all"] and args.dataset2:
            print("Performing dataset comparison...")
            comparison_results = compare_datasets(dataset1, dataset2)
            results["comparison"] = comparison_results
            if "correlation" in comparison_results:
                corr = comparison_results["correlation"].get("pearson_r", "N/A")
                print(f"Correlation: {corr:.3f}")

        # Save results
        if args.output:
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)

            output_path = output_dir / "analysis_results.json"
            save_results(results, output_path, format="json")
            print(f"Results saved to: {output_path}")

        print("Analysis completed successfully!")

    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()