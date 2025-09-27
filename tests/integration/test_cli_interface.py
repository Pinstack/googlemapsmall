"""Integration tests for CLI interface.

Tests the command-line interface for the Google Maps Mall Scraper.
These tests MUST FAIL initially (no CLI implementation yet) - TDD approach.
"""

import json
import subprocess
import tempfile
from pathlib import Path


class TestCLIInterface:
    """Test cases for CLI interface functionality."""

    def test_cli_basic_scraping_command(self) -> None:
        """Test basic scraping command via CLI."""
        # This test will fail until cli.py is implemented
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "output.json"

            # Run CLI command (will fail initially)
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "src.cli",
                    "scrape",
                    "https://www.google.com/maps/place/St+James+Quarter",
                    "--output",
                    str(output_file),
                    "--strategy",
                    "view_all",
                ],
                capture_output=True,
                text=True,
                cwd=".",
            )

            # Should succeed
            assert result.returncode == 0

            # Should create output file
            assert output_file.exists()

            # Should contain valid JSON
            with open(output_file, "r") as f:
                data = json.load(f)

            # Should have expected structure
            assert "brands" in data
            assert "categories" in data
            assert "metadata" in data
            assert len(data["brands"]) > 0

    def test_cli_category_strategy(self) -> None:
        """Test category-based scraping via CLI."""
        # This test will fail until cli.py is implemented
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "output.json"

            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "src.cli",
                    "scrape",
                    "https://www.google.com/maps/place/St+James+Quarter",
                    "--output",
                    str(output_file),
                    "--strategy",
                    "categories",
                    "--max-categories",
                    "3",
                ],
                capture_output=True,
                text=True,
                cwd=".",
            )

            assert result.returncode == 0
            assert output_file.exists()

            with open(output_file, "r") as f:
                data = json.load(f)

            assert "categories" in data
            assert len(data["categories"]) <= 3  # Should respect max-categories
            assert all(cat["brand_count"] >= 0 for cat in data["categories"])

    def test_cli_output_formats(self) -> None:
        """Test different output formats."""
        # This test will fail until cli.py is implemented
        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = Path(temp_dir) / "output.json"
            csv_file = Path(temp_dir) / "output.csv"

            # Test JSON output
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "src.cli",
                    "scrape",
                    "https://www.google.com/maps/place/Test+Mall",
                    "--output",
                    str(json_file),
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                cwd=".",
            )

            assert result.returncode == 0
            assert json_file.exists()

            with open(json_file, "r") as f:
                json.load(f)  # Should be valid JSON

            # Test CSV output (if supported)
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "src.cli",
                    "scrape",
                    "https://www.google.com/maps/place/Test+Mall",
                    "--output",
                    str(csv_file),
                    "--format",
                    "csv",
                ],
                capture_output=True,
                text=True,
                cwd=".",
            )

            # CSV might not be implemented yet, so check return code
            if result.returncode == 0:
                assert csv_file.exists()

    def test_cli_error_handling(self) -> None:
        """Test CLI error handling for invalid inputs."""
        # This test will fail until cli.py is implemented

        # Test invalid URL
        result = subprocess.run(
            [
                "python",
                "-m",
                "src.cli",
                "scrape",
                "invalid-url",
                "--output",
                "test.json",
            ],
            capture_output=True,
            text=True,
            cwd=".",
        )

        # Should fail gracefully
        assert result.returncode != 0
        assert "error" in result.stderr.lower() or "invalid" in result.stderr.lower()

        # Test missing required arguments
        result = subprocess.run(
            ["python", "-m", "src.cli", "scrape"],
            capture_output=True,
            text=True,
            cwd=".",
        )

        # Should show help or error
        assert result.returncode != 0

    def test_cli_help_and_version(self) -> None:
        """Test CLI help and version commands."""
        # This test will fail until cli.py is implemented

        # Test help command
        result = subprocess.run(
            ["python", "-m", "src.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=".",
        )

        assert result.returncode == 0
        assert "usage" in result.stdout.lower() or "help" in result.stdout.lower()

        # Test version command
        result = subprocess.run(
            ["python", "-m", "src.cli", "--version"],
            capture_output=True,
            text=True,
            cwd=".",
        )

        assert result.returncode == 0
        assert "1.0" in result.stdout or "version" in result.stdout.lower()

    def test_cli_configuration_options(self) -> None:
        """Test CLI configuration options."""
        # This test will fail until cli.py is implemented
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "output.json"

            # Test with timeout configuration
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "src.cli",
                    "scrape",
                    "https://www.google.com/maps/place/Test+Mall",
                    "--output",
                    str(output_file),
                    "--timeout",
                    "30",
                    "--strategy",
                    "view_all",
                ],
                capture_output=True,
                text=True,
                cwd=".",
            )

            assert result.returncode == 0
            assert output_file.exists()

    def test_cli_har_analysis_command(self) -> None:
        """Test HAR analysis command via CLI."""
        # This test will fail until cli.py is implemented
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "analysis.json"
            har_file = "googlemaps.har"  # Assume HAR file exists

            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "src.cli",
                    "analyze",
                    har_file,
                    "--output",
                    str(output_file),
                ],
                capture_output=True,
                text=True,
                cwd=".",
            )

            if har_file and Path(har_file).exists():
                assert result.returncode == 0
                assert output_file.exists()

                with open(output_file, "r") as f:
                    data = json.load(f)

                # Should contain HAR analysis results
                assert "network_requests" in data
                assert "protobuf_endpoints" in data
            else:
                # If no HAR file, should show appropriate error
                assert result.returncode != 0

    def test_cli_verbose_output(self) -> None:
        """Test verbose output option."""
        # This test will fail until cli.py is implemented
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "output.json"

            # Test with verbose flag
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "src.cli",
                    "--verbose",
                    "scrape",
                    "https://www.google.com/maps/place/Test+Mall",
                    "--output",
                    str(output_file),
                    "--strategy",
                    "view_all",
                ],
                capture_output=True,
                text=True,
                cwd=".",
            )

            assert result.returncode == 0

            # Verbose output should show progress information
            assert "scraping" in result.stdout.lower() or len(result.stdout) > 100

    def test_cli_invalid_strategy_error(self) -> None:
        """Test error handling for invalid scraping strategy."""
        # This test will fail until cli.py is implemented
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "output.json"

            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "src.cli",
                    "scrape",
                    "https://www.google.com/maps/place/Test+Mall",
                    "--output",
                    str(output_file),
                    "--strategy",
                    "invalid_strategy",
                ],
                capture_output=True,
                text=True,
                cwd=".",
            )

            # Should fail with invalid strategy
            assert result.returncode != 0
            assert (
                "strategy" in result.stderr.lower()
                or "invalid" in result.stderr.lower()
            )
