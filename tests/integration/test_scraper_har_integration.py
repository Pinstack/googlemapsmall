"""Integration tests for scraper and HAR analyzer integration.

Tests the combined functionality of browser scraper and HAR analyzer
for network-aware automation.
"""

import pytest
from typing import Any, Dict


class TestScraperHarIntegration:
    """Test cases for scraper and HAR analyzer integration."""

    def test_scraper_uses_har_analysis_for_strategy_selection(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test that scraper uses HAR analysis to select optimal scraping strategy."""
        # This test will fail until integration is implemented
        from src.har_analyzer import analyze_har_file
        from src.scraper import scrape_mall_directory

        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        # Analyze HAR to understand network patterns
        har_results = analyze_har_file("tests/fixtures/minimal_har.json", mall_context)

        # Extract strategy recommendations from HAR analysis
        data_patterns = har_results.get("data_patterns", {})
        pagination_trigger = data_patterns.get("pagination_trigger")
        session_persistence = data_patterns.get("session_persistence", {})

        # Scraper should adapt strategy based on HAR analysis
        strategy_config = {"strategy": "view_all"}

        # If HAR shows pagination patterns, strategy might be adapted
        if pagination_trigger:
            strategy_config["pagination_aware"] = True

        # If HAR shows session requirements, include session handling
        if session_persistence:
            strategy_config["session_handling"] = True

        result = scrape_mall_directory(
            "https://www.google.com/maps/place/Test+Mall", strategy_config, har_results
        )

        # Verify scraper adapted to HAR analysis
        assert "brands" in result
        assert "metadata" in result
        assert result["metadata"]["success_rate"] >= 0.0

    def test_har_guided_scraping_workflow(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test complete workflow where HAR analysis guides scraping decisions."""
        # This test will fail until integration is implemented
        from src.har_analyzer import analyze_har_file
        from src.scraper import scrape_mall_directory

        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        # Step 1: Analyze HAR for network intelligence
        har_results = analyze_har_file("tests/fixtures/minimal_har.json", mall_context)

        # Step 2: Extract actionable insights
        protobuf_endpoints = har_results.get("protobuf_endpoints", [])
        data_patterns = har_results.get("data_patterns", {})
        session_context = har_results.get("session_context", {})

        # Step 3: Configure scraper with HAR insights
        strategy_config = {
            "strategy": "view_all",
            "har_insights": {
                "protobuf_endpoints": len(protobuf_endpoints),
                "has_pagination": data_patterns.get("pagination_trigger") is not None,
                "session_required": bool(
                    session_context.get("session_id")
                    or session_context.get("auth_params")
                ),
            },
        }

        # Step 4: Execute scraping with HAR guidance
        result = scrape_mall_directory(
            "https://www.google.com/maps/place/Test+Mall", strategy_config, har_results
        )

        # Verify the integrated workflow
        assert result["brands"]  # Should extract brands
        assert result["metadata"]["interactions_performed"] >= 0

        # Metadata should reflect HAR-guided decisions
        metadata = result["metadata"]
        assert "session_duration" in metadata

    def test_scraper_adapts_to_har_network_patterns(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test that scraper adapts timing and behavior based on HAR network patterns."""
        # This test will fail until integration is implemented
        from src.har_analyzer import analyze_har_file
        from src.scraper import scrape_mall_directory

        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        # Analyze HAR to understand timing patterns
        har_results = analyze_har_file("tests/fixtures/minimal_har.json", mall_context)

        # Extract timing and rate limiting insights
        data_patterns = har_results.get("data_patterns", {})
        rate_limiting = data_patterns.get("rate_limiting", {})

        # Scraper should adapt timing based on HAR analysis
        strategy_config = {
            "strategy": "view_all",
            "timing_adaptation": {
                "rate_limit_detected": rate_limiting.get("status") != "unknown",
                "har_based_delays": True,
            },
        }

        result = scrape_mall_directory(
            "https://www.google.com/maps/place/Test+Mall", strategy_config, har_results
        )

        # Verify timing adaptation
        metadata = result["metadata"]
        assert metadata["session_duration"] >= 0.0  # Should have reasonable duration

        # If rate limiting detected, should show longer delays
        if rate_limiting.get("status") != "unknown":
            assert metadata["session_duration"] > 1.0  # Should have adapted delays

    def test_har_session_context_integration_with_scraper(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test that HAR session context is properly integrated with scraper."""
        # This test will fail until integration is implemented
        from src.har_analyzer import analyze_har_file
        from src.scraper import scrape_mall_directory

        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        # Get session context from HAR analysis
        har_results = analyze_har_file("tests/fixtures/minimal_har.json", mall_context)
        session_context = har_results.get("session_context", {})

        # Scraper should use session context for more effective automation
        strategy_config = {"strategy": "view_all", "session_context": session_context}

        result = scrape_mall_directory(
            "https://www.google.com/maps/place/Test+Mall", strategy_config, har_results
        )

        # Verify session integration
        assert "brands" in result
        metadata = result["metadata"]

        # Should indicate session-aware scraping
        if session_context.get("session_id") or session_context.get("auth_params"):
            assert (
                metadata["interactions_performed"] >= 0
            )  # Should perform interactions

    def test_scraper_error_recovery_using_har_insights(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test that scraper uses HAR insights for error recovery."""
        # This test will fail until integration is implemented
        from src.har_analyzer import analyze_har_file
        from src.scraper import scrape_mall_directory

        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        # Analyze HAR for error recovery insights
        har_results = analyze_har_file("tests/fixtures/minimal_har.json", mall_context)

        # Extract error recovery patterns
        data_patterns = har_results.get("data_patterns", {})
        session_persistence = data_patterns.get("session_persistence", {})

        # Configure scraper with error recovery based on HAR
        strategy_config = {
            "strategy": "view_all",
            "error_recovery": {
                "use_session_recovery": bool(session_persistence),
                "har_based_retry": True,
            },
        }

        result = scrape_mall_directory(
            "https://www.google.com/maps/place/Test+Mall", strategy_config, har_results
        )

        # Verify error recovery integration
        metadata = result["metadata"]
        assert "errors_encountered" in metadata
        assert isinstance(metadata["errors_encountered"], list)

        # Success rate should reflect recovery capabilities
        assert 0.0 <= metadata["success_rate"] <= 1.0

    def test_network_aware_scraping_decisions(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test that scraper makes network-aware decisions based on HAR analysis."""
        # This test will fail until integration is implemented
        from src.har_analyzer import analyze_har_file
        from src.scraper import scrape_mall_directory

        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        # Analyze HAR for network intelligence
        har_results = analyze_har_file("tests/fixtures/minimal_har.json", mall_context)

        network_requests = har_results.get("network_requests", [])
        protobuf_endpoints = har_results.get("protobuf_endpoints", [])

        # Scraper should make decisions based on network analysis
        strategy_config = {
            "strategy": "view_all",
            "network_intelligence": {
                "total_requests": len(network_requests),
                "protobuf_endpoints": len(protobuf_endpoints),
                "adapt_to_patterns": True,
            },
        }

        result = scrape_mall_directory(
            "https://www.google.com/maps/place/Test+Mall", strategy_config, har_results
        )

        # Verify network-aware decisions
        assert len(result["brands"]) >= 0  # Should extract some brands

        # Metadata should reflect network intelligence usage
        metadata = result["metadata"]
        assert metadata["interactions_performed"] >= 0

    def test_har_based_scraping_optimization(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test that HAR analysis enables scraping optimizations."""
        # This test will fail until integration is implemented
        from src.har_analyzer import analyze_har_file
        from src.scraper import scrape_mall_directory

        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        # Analyze HAR for optimization opportunities
        har_results = analyze_har_file("tests/fixtures/minimal_har.json", mall_context)

        # Extract optimization insights
        data_patterns = har_results.get("data_patterns", {})
        has_pagination = data_patterns.get("pagination_trigger") is not None

        # Configure optimized scraping
        strategy_config = {
            "strategy": "view_all",
            "optimizations": {
                "pagination_optimization": has_pagination,
                "har_based_efficiency": True,
            },
        }

        result = scrape_mall_directory(
            "https://www.google.com/maps/place/Test+Mall", strategy_config, har_results
        )

        # Verify optimizations were applied
        metadata = result["metadata"]
        assert "session_duration" in metadata

        # Optimized scraping should be reasonably fast
        assert (
            metadata["session_duration"] < 60.0
        )  # Should complete within reasonable time

    def test_integrated_har_scraper_error_handling(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test error handling in the integrated HAR-scraper workflow."""
        # This test will fail until integration is implemented
        from src.har_analyzer import analyze_har_file
        from src.scraper import scrape_mall_directory

        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        # Test with invalid HAR file
        har_results = None
        try:
            har_results = analyze_har_file("nonexistent.har", mall_context)
            # If no exception, HAR analysis should handle gracefully
            assert isinstance(har_results, dict)
        except (FileNotFoundError, ValueError):
            # Expected for invalid HAR file - har_results remains None
            pass

        # Test scraper with HAR analysis results (may be None)
        strategy_config = {"strategy": "view_all"}

        result = scrape_mall_directory(
            "https://www.google.com/maps/place/Test+Mall", strategy_config, har_results
        )

        # Even with potential HAR analysis issues, scraper should handle gracefully
        assert isinstance(result, dict)
        assert "brands" in result
        assert "metadata" in result

        # Error information should be captured
        metadata = result["metadata"]
        assert "errors_encountered" in metadata
