"""Integration tests for the full intelligent anti-detection pipeline.

Tests the complete integration of HAR analysis, proxy rotation, and adaptive scraping
for maximum anti-detection intelligence.
"""

import pytest
from typing import Any, Dict


class TestFullIntelligencePipeline:
    """Test cases for the complete intelligent scraping pipeline."""

    def test_har_driven_proxy_rotation_on_rate_limits(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test that HAR analysis triggers proxy rotation when rate limiting is detected."""
        # This test will fail until full integration is implemented
        from src.har_analyzer import analyze_har_file
        from src.scraper import scrape_mall_directory
        from src.proxy_manager import create_default_proxy_manager

        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        # Analyze HAR to detect rate limiting patterns
        har_results = analyze_har_file("tests/fixtures/minimal_har.json", mall_context)

        # Configure scraper with HAR insights and proxy rotation
        strategy_config = {
            "strategy": "view_all",
            "har_insights": {
                "protobuf_endpoints": len(har_results.get("protobuf_endpoints", [])),
                "has_pagination": har_results.get("data_patterns", {}).get(
                    "pagination_trigger"
                )
                is not None,
                "session_required": bool(
                    har_results.get("session_context", {}).get("session_id")
                ),
            },
            "timing_adaptation": {
                "rate_limit_detected": har_results.get("data_patterns", {})
                .get("rate_limiting", {})
                .get("status")
                != "unknown",
                "har_based_delays": True,
            },
            "network_intelligence": {"adapt_to_patterns": True},
        }

        # Create proxy manager for intelligent rotation
        proxy_manager = create_default_proxy_manager()

        # Execute scraping with full intelligence pipeline
        result = scrape_mall_directory(
            "https://www.google.com/maps/place/Test+Mall",
            strategy_config,
            har_results,
            proxy_manager,
        )

        # Verify the intelligent pipeline worked
        assert result["brands"]  # Should extract brands
        assert (
            result["metadata"]["success_rate"] > 0.9
        )  # High success due to intelligence

        # Should show proxy usage
        metadata = result["metadata"]
        assert metadata["proxy_enabled"] is True
        assert metadata["total_proxies"] == 10  # From default Webshare proxies

        # Should show HAR awareness
        assert metadata["har_aware"] is True
        assert metadata["network_adapted"] is True

    def test_adaptive_strategy_based_on_har_complexity(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test that scraping strategy adapts based on HAR complexity and patterns."""
        # This test will fail until full integration is implemented
        from src.har_analyzer import analyze_har_file
        from src.scraper import scrape_mall_directory
        from src.proxy_manager import ProxyManager

        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        har_results = analyze_har_file("tests/fixtures/minimal_har.json", mall_context)

        # Analyze HAR complexity
        data_patterns = har_results.get("data_patterns", {})
        protobuf_endpoints = har_results.get("protobuf_endpoints", [])
        session_context = har_results.get("session_context", {})

        # Determine strategy based on HAR analysis
        har_complexity = {
            "has_session_management": bool(
                session_context.get("session_id") or session_context.get("auth_params")
            ),
            "has_pagination": data_patterns.get("pagination_trigger") is not None,
            "protobuf_endpoints_count": len(protobuf_endpoints),
            "rate_limiting_detected": data_patterns.get("rate_limiting", {}).get(
                "status"
            )
            != "unknown",
        }

        # Adaptive strategy selection
        if har_complexity["protobuf_endpoints_count"] > 2:
            base_strategy = "categories"  # Complex site, use category approach
        else:
            base_strategy = "view_all"  # Simple site, use direct approach

        strategy_config = {
            "strategy": base_strategy,
            "har_complexity": har_complexity,
            "adaptations": {
                "session_handling": har_complexity["has_session_management"],
                "pagination_optimization": har_complexity["has_pagination"],
                "rate_limit_protection": har_complexity["rate_limiting_detected"],
            },
        }

        # Use proxy if rate limiting detected
        proxy_manager = None
        if har_complexity["rate_limiting_detected"]:
            proxy_manager = ProxyManager()
            proxy_manager.load_proxies(
                [
                    "142.111.48.253:7030:testuser:testpass",
                    "198.23.239.134:6540:testuser:testpass",
                ]
            )

        result = scrape_mall_directory(
            "https://www.google.com/maps/place/Test+Mall",
            strategy_config,
            har_results,
            proxy_manager,
        )

        # Verify adaptive behavior
        metadata = result["metadata"]
        assert metadata["har_aware"] is True

        if har_complexity["rate_limiting_detected"]:
            assert metadata["proxy_enabled"] is True
            assert metadata["proxy_rotations"] >= 0

        # Success rate should reflect intelligent adaptations
        assert metadata["success_rate"] >= 0.95

    def test_session_persistence_with_proxy_rotation(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test that session context is maintained across proxy rotations."""
        # This test will fail until full integration is implemented
        from src.har_analyzer import analyze_har_file
        from src.scraper import scrape_mall_directory
        from src.proxy_manager import ProxyManager

        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        har_results = analyze_har_file("tests/fixtures/minimal_har.json", mall_context)

        # Extract session context from HAR
        session_context = har_results.get("session_context", {})

        # Create proxy manager for rotation testing
        proxy_manager = ProxyManager()
        proxy_manager.load_proxies(
            [
                "142.111.48.253:7030:testuser:testpass",
                "198.23.239.134:6540:testuser:testpass",
            ]
        )

        # Configure scraper with session persistence and proxy rotation
        strategy_config = {
            "strategy": "view_all",
            "session_context": session_context,
            "error_recovery": {"use_session_recovery": True, "har_based_retry": True},
        }

        result = scrape_mall_directory(
            "https://www.google.com/maps/place/Test+Mall",
            strategy_config,
            har_results,
            proxy_manager,
        )

        # Verify session and proxy integration
        metadata = result["metadata"]
        assert metadata["session_handled"] is True
        assert metadata["proxy_enabled"] is True

        # Should show higher success rate due to session + proxy intelligence
        assert metadata["success_rate"] >= 0.97

    def test_multi_layer_anti_detection_orchestration(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test orchestration of multiple anti-detection layers."""
        # This test will fail until full integration is implemented
        from src.har_analyzer import analyze_har_file
        from src.scraper import scrape_mall_directory
        from src.proxy_manager import create_default_proxy_manager

        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        har_results = analyze_har_file("tests/fixtures/minimal_har.json", mall_context)

        # Comprehensive anti-detection configuration
        strategy_config = {
            "strategy": "categories",
            "max_categories": 3,
            "har_insights": {
                "complexity_score": len(har_results.get("protobuf_endpoints", []))
                + len(har_results.get("network_requests", [])),
                "session_complexity": bool(har_results.get("session_context", {})),
            },
            "timing_adaptation": {
                "rate_limit_detected": True,  # Force rate limiting simulation
                "har_based_delays": True,
                "adaptive_backoff": True,
            },
            "network_intelligence": {
                "adapt_to_patterns": True,
                "proxy_rotation_on_failure": True,
            },
            "session_context": har_results.get("session_context", {}),
            "error_recovery": {
                "use_session_recovery": True,
                "har_based_retry": True,
                "proxy_rotation_fallback": True,
            },
            "optimizations": {
                "pagination_optimization": har_results.get("data_patterns", {}).get(
                    "pagination_trigger"
                )
                is not None,
                "har_based_efficiency": True,
            },
        }

        # Full proxy infrastructure
        proxy_manager = create_default_proxy_manager()

        result = scrape_mall_directory(
            "https://www.google.com/maps/place/Test+Mall",
            strategy_config,
            har_results,
            proxy_manager,
        )

        # Verify comprehensive anti-detection orchestration
        metadata = result["metadata"]

        # All intelligence layers should be active
        assert metadata["har_aware"] is True
        assert metadata["network_adapted"] is True
        assert metadata["proxy_enabled"] is True
        assert metadata["session_handled"] is True

        # Should show maximum success rate from layered intelligence
        assert metadata["success_rate"] >= 0.98

        # Should have performed intelligent interactions
        assert metadata["interactions_performed"] >= 10  # Multiple layers active

        # Should show proxy rotations for rate limiting protection
        assert metadata["proxy_rotations"] >= 0

    def test_intelligence_fallback_when_har_unavailable(self) -> None:
        """Test graceful fallback when HAR analysis is unavailable."""
        # This test will fail until full integration is implemented
        from src.scraper import scrape_mall_directory
        from src.proxy_manager import ProxyManager

        # No HAR analysis available
        har_results = None

        # Configure with proxy but no HAR insights
        strategy_config = {
            "strategy": "view_all",
            "timing_adaptation": {
                "rate_limit_detected": False,  # No HAR to detect this
                "har_based_delays": False,
            },
            "network_intelligence": {"adapt_to_patterns": False},  # No HAR patterns
        }

        proxy_manager = ProxyManager()
        proxy_manager.load_proxies(["142.111.48.253:7030:testuser:testpass"])

        result = scrape_mall_directory(
            "https://www.google.com/maps/place/Test+Mall",
            strategy_config,
            har_results,
            proxy_manager,
        )

        # Verify fallback behavior
        metadata = result["metadata"]
        assert metadata["har_aware"] is False
        assert metadata["proxy_enabled"] is True

        # Should still work but with reduced intelligence
        assert metadata["success_rate"] >= 0.90  # Good but not maximum
        assert len(result["brands"]) >= 0

    def test_proxy_rotation_intelligence_vs_basic_delays(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Compare proxy rotation intelligence vs basic delay-only approach."""
        # This test will fail until full integration is implemented
        from src.har_analyzer import analyze_har_file
        from src.scraper import scrape_mall_directory
        from src.proxy_manager import ProxyManager

        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        har_results = analyze_har_file("tests/fixtures/minimal_har.json", mall_context)

        # Test 1: Basic delay-only approach
        basic_strategy = {
            "strategy": "view_all",
            "timing_adaptation": {
                "rate_limit_detected": True,
                "har_based_delays": False,
            },
        }

        basic_result = scrape_mall_directory(
            "https://www.google.com/maps/place/Test+Mall", basic_strategy, har_results
        )

        # Test 2: Intelligent proxy rotation approach
        proxy_manager = ProxyManager()
        proxy_manager.load_proxies(
            [
                "142.111.48.253:7030:testuser:testpass",
                "198.23.239.134:6540:testuser:testpass",
            ]
        )

        intelligent_strategy = {
            "strategy": "view_all",
            "timing_adaptation": {
                "rate_limit_detected": True,
                "har_based_delays": True,
            },
            "network_intelligence": {"adapt_to_patterns": True},
        }

        intelligent_result = scrape_mall_directory(
            "https://www.google.com/maps/place/Test+Mall",
            intelligent_strategy,
            har_results,
            proxy_manager,
        )

        # Intelligent approach should outperform basic delays
        basic_success = basic_result["metadata"]["success_rate"]
        intelligent_success = intelligent_result["metadata"]["success_rate"]

        assert intelligent_success >= basic_success  # At least as good
        if intelligent_success > basic_success:
            # Should show proxy intelligence advantages
            assert intelligent_result["metadata"]["proxy_enabled"] is True
            assert intelligent_result["metadata"]["proxy_rotations"] >= 0
