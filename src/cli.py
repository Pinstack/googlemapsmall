"""Command Line Interface for Google Maps Mall Scraper.

Provides a command-line interface to scrape Google Maps mall directories
and analyze HAR files for network patterns.
"""  # noqa: E501

import argparse
import json
import sys
from pathlib import Path


def setup_imports() -> None:
    """Setup module imports for both package and direct execution."""
    global scraper, analyze_har_file

    # Always add src directory to path for consistent imports
    src_dir = Path(__file__).parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    # Import modules
    import scraper as scraper_module
    from har_analyzer import analyze_har_file as analyze_func

    scraper = scraper_module
    analyze_har_file = analyze_func


def main() -> int:
    """Main CLI entry point."""
    # Setup imports - handle both package and direct execution
    setup_imports()

    parser = create_parser()
    args = parser.parse_args()

    if not hasattr(args, "command"):
        parser.print_help()
        return 1

    try:
        if args.command == "scrape":
            return handle_scrape_command(args)
        elif args.command == "analyze":
            return handle_analyze_command(args)
        else:
            parser.print_help()
            return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="googlemaps-mall-scraper",
        description="Scrape Google Maps mall directories and analyze network patterns",
    )

    parser.add_argument(
        "--version", action="version", version="Google Maps Mall Scraper 1.0"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scrape command
    scrape_parser = subparsers.add_parser(
        "scrape", help="Scrape a Google Maps mall directory"
    )
    scrape_parser.add_argument("url", help="Google Maps URL for the mall to scrape")
    scrape_parser.add_argument(
        "--output", "-o", required=True, help="Output file path (JSON format)"
    )
    scrape_parser.add_argument(
        "--strategy",
        "-s",
        choices=["view_all", "categories"],
        default="view_all",
        help="Scraping strategy (default: view_all)",
    )
    scrape_parser.add_argument(
        "--max-categories",
        type=int,
        default=10,
        help="Maximum categories to scrape (for categories strategy)",
    )
    scrape_parser.add_argument(
        "--format",
        "-f",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)",
    )
    scrape_parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Scraping timeout in seconds (default: 120)",
    )

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze HAR file for network patterns"
    )
    analyze_parser.add_argument("har_file", help="Path to HAR file to analyze")
    analyze_parser.add_argument(
        "--output", "-o", required=True, help="Output file path for analysis results"
    )

    return parser


def handle_scrape_command(args: argparse.Namespace) -> int:
    """Handle the scrape command."""
    if args.verbose:
        print(f"Scraping mall: {args.url}")
        print(f"Strategy: {args.strategy}")
        print(f"Output: {args.output}")

    # Validate URL
    if not args.url.startswith("http"):
        print(f"Error: Invalid URL: {args.url}", file=sys.stderr)
        return 1

    # Prepare strategy configuration
    strategy_config = {"strategy": args.strategy}
    if args.strategy == "categories":
        strategy_config["max_categories"] = args.max_categories

    try:
        # Perform scraping
        if args.verbose:
            print("Starting scraper...")

        result = scraper.scrape_mall_directory(args.url, strategy_config)

        if args.verbose:
            print(f"Scraping completed. Found {len(result['brands'])} brands.")

        # Save results
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if args.format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        elif args.format == "csv":
            # For now, just save JSON (CSV not implemented yet)
            print(
                "Warning: CSV format not implemented yet, saving as JSON",
                file=sys.stderr,
            )
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

        if args.verbose:
            print(f"Results saved to: {args.output}")

        return 0

    except Exception as e:
        print(f"Scraping failed: {e}", file=sys.stderr)
        return 1


def handle_analyze_command(args: argparse.Namespace) -> int:
    """Handle the analyze command."""
    if args.verbose:
        print(f"Analyzing HAR file: {args.har_file}")
        print(f"Output: {args.output}")

    har_path = Path(args.har_file)
    if not har_path.exists():
        print(f"Error: HAR file not found: {args.har_file}", file=sys.stderr)
        return 1

    try:
        # Create mall context (minimal for POC)
        mall_context = {
            "mall_id": "test_mall",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        # Perform analysis
        if args.verbose:
            print("Starting HAR analysis...")

        result = analyze_har_file(str(har_path), mall_context)

        if args.verbose:
            print(
                f"Analysis completed. Found {len(result['network_requests'])} network requests."
            )

        # Save results
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        if args.verbose:
            print(f"Analysis results saved to: {args.output}")

        return 0

    except Exception as e:
        print(f"Analysis failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
