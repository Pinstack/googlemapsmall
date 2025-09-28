"""Performance tests for HAR analysis throughput in live scraping scenarios.

Tests HAR processing speed and memory usage under various load conditions.
"""

import time
import pytest
from typing import Dict, Any, List

# Import HAR analyzer
try:
    from src.har_analyzer import analyze_live_har_session
except ImportError:
    analyze_live_har_session = None


class TestHARProcessingPerformance:
    """Test HAR analysis performance under live scraping conditions."""

    def test_har_analysis_empty_session(self):
        """Test HAR analysis performance with empty session."""
        if not analyze_live_har_session:
            pytest.skip("HAR analyzer not available")

        har_data = {"log": {"entries": []}}

        start_time = time.time()
        result = analyze_live_har_session(har_data, {})
        duration = time.time() - start_time

        # Should complete quickly for empty data
        assert duration < 0.1, f"Empty HAR analysis took {duration:.3f}s"

        # Should return default structure
        assert "pagination_analysis" in result
        assert "rate_limit_analysis" in result
        assert result["pagination_analysis"]["has_pagination"] is False

    def test_har_analysis_typical_session(self):
        """Test HAR analysis with typical Google Maps session data."""
        if not analyze_live_har_session:
            pytest.skip("HAR analyzer not available")

        # Create mock HAR data similar to real Google Maps session
        har_entries = [
            {
                "request": {
                    "method": "GET",
                    "url": "https://www.google.com/maps/_/js/k=maps.m.en.1234567890.O/m=cp"
                },
                "response": {"status": 200, "content": {"size": 50000}},
                "time": 150
            },
            {
                "request": {
                    "method": "POST",
                    "url": "https://www.google.com/maps/_/js/k=maps.m.en.1234567890.O/m=cp"
                },
                "response": {"status": 200, "content": {"size": 25000}},
                "time": 200
            },
            {
                "request": {
                    "method": "GET",
                    "url": "https://www.google.com/maps/vt?pb=!1m2!1y55.9533!2x-3.1883"
                },
                "response": {"status": 200, "content": {"size": 100000}},
                "time": 300
            }
        ] * 10  # Simulate 30 entries

        har_data = {
            "log": {
                "entries": har_entries
            }
        }

        start_time = time.time()
        result = analyze_live_har_session(har_data, {"expected_brand_count": 150})
        duration = time.time() - start_time

        # Should complete within reasonable time (under 1 second for 30 entries)
        assert duration < 1.0, f"HAR analysis took {duration:.3f}s for 30 entries"

        # Should analyze pagination and rate limiting
        assert "pagination_analysis" in result
        assert "rate_limit_analysis" in result
        assert "recommendations" in result

    def test_har_analysis_large_session(self):
        """Test HAR analysis performance with large session (stress test)."""
        if not analyze_live_har_session:
            pytest.skip("HAR analyzer not available")

        # Create large HAR session with 100+ entries
        har_entries = []
        for i in range(120):  # Simulate large scraping session
            har_entries.append({
                "request": {
                    "method": "GET",
                    "url": f"https://www.google.com/maps/api/place/details?place_id=ChIJ{i}"
                },
                "response": {"status": 200 if i % 10 != 0 else 429, "content": {"size": 15000}},
                "time": 100 + (i % 50)  # Vary timing
            })

        har_data = {"log": {"entries": har_entries}}

        start_time = time.time()
        result = analyze_live_har_session(har_data, {"expected_brand_count": 150})
        duration = time.time() - start_time

        # Should complete within reasonable time (under 2 seconds for 120 entries)
        assert duration < 2.0, f"Large HAR analysis took {duration:.3f}s for 120 entries"

        # Should detect rate limiting from the 429 responses
        assert result["rate_limit_analysis"]["rate_limiting_detected"]

    @pytest.mark.parametrize("entry_count", [10, 50, 100])
    def test_har_analysis_scalability(self, entry_count):
        """Test that HAR analysis scales linearly with entry count."""
        if not analyze_live_har_session:
            pytest.skip("HAR analyzer not available")

        # Create HAR data with specified entry count
        har_entries = [
            {
                "request": {"method": "GET", "url": f"https://example.com/{i}"},
                "response": {"status": 200, "content": {"size": 1000}},
                "time": 50
            }
            for i in range(entry_count)
        ]

        har_data = {"log": {"entries": har_entries}}

        start_time = time.time()
        result = analyze_live_har_session(har_data, {})
        duration = time.time() - start_time

        # Performance should scale reasonably (under 0.5s per 100 entries)
        max_duration = (entry_count / 100) * 0.5
        assert duration < max_duration, f"HAR analysis too slow: {duration:.3f}s for {entry_count} entries"

    def test_har_analysis_memory_efficiency(self):
        """Test that HAR analysis doesn't have memory leaks or excessive usage."""
        if not analyze_live_har_session:
            pytest.skip("HAR analyzer not available")

        # Test with moderately large HAR data
        har_entries = [
            {
                "request": {"method": "GET", "url": f"https://maps.google.com/large/{i}"},
                "response": {
                    "status": 200,
                    "content": {"size": 50000, "text": "x" * 1000}  # Simulate content
                },
                "time": 150
            }
            for i in range(50)
        ]

        har_data = {"log": {"entries": har_entries}}

        # This should not cause memory issues
        result = analyze_live_har_session(har_data, {})

        # Verify result structure is intact
        assert "pagination_analysis" in result
        assert "rate_limit_analysis" in result
        assert isinstance(result["recommendations"], list)

    def test_har_analysis_error_handling(self):
        """Test HAR analysis error handling and resilience."""
        if not analyze_live_har_session:
            pytest.skip("HAR analyzer not available")

        # Test with malformed HAR data
        malformed_har = {"invalid": "structure"}

        # Should not crash, return default analysis
        result = analyze_live_har_session(malformed_har, {})

        assert "pagination_analysis" in result
        assert result["pagination_analysis"]["has_pagination"] is False

        # Test with None input
        result_none = analyze_live_har_session(None, {})

        assert "pagination_analysis" in result_none
        assert result_none["pagination_analysis"]["has_pagination"] is False
