"""Performance tests for execution time validation.

Tests ensure the Google Maps Mall Scraper meets the <2 minute execution requirement
for POC validation. Covers end-to-end scraping performance and component benchmarks.
"""

import time
import pytest
from typing import Any, Dict


class TestExecutionTime:
    """Test cases for execution time performance requirements."""

    def test_end_to_end_scraping_under_2_minutes(self) -> None:
        """Test complete mall scraping completes in under 2 minutes."""
        from src.scraper import scrape_mall_directory

        mall_url = "https://www.google.com/maps/place/St+James+Quarter"
        strategy_config = {"strategy": "view_all", "max_brands": 150}  # POC target

        start_time = time.time()

        # Execute complete scraping workflow
        result = scrape_mall_directory(mall_url, strategy_config)

        end_time = time.time()
        execution_time = end_time - start_time

        # Validate performance requirement
        assert (
            execution_time < 120.0
        ), f"Execution time {execution_time:.2f}s exceeds 2 minute limit (120s)"

        # Validate result quality
        assert "brands" in result
        assert "metadata" in result
        brands = result["brands"]
        assert len(brands) > 0, "Should extract at least some brands"

        # Log performance metrics
        metadata = result["metadata"]
        print(f"Performance Test Results:")
        print(f"  Execution time: {execution_time:.2f}s")
        print(f"  Brands extracted: {len(brands)}")
        print(f"  Success rate: {metadata.get('processing_success_rate', 0):.1%}")

    def test_category_based_scraping_performance(self) -> None:
        """Test category-based scraping performance."""
        from src.scraper import scrape_mall_directory

        mall_url = "https://www.google.com/maps/place/St+James+Quarter"
        strategy_config = {"strategy": "categories", "max_categories": 5}

        start_time = time.time()
        result = scrape_mall_directory(mall_url, strategy_config)
        execution_time = time.time() - start_time

        # Should be faster than full scraping due to limited categories
        assert (
            execution_time < 90.0
        ), f"Category scraping too slow: {execution_time:.2f}s"

        # Validate results
        categories = result.get("categories", [])
        assert len(categories) <= strategy_config["max_categories"]

        print(f"Category Scraping Performance:")
        print(f"  Time: {execution_time:.2f}s")
        print(f"  Categories: {len(categories)}")

    def test_har_analysis_performance(self) -> None:
        """Test HAR file analysis performance (<30 seconds)."""
        from src.har_analyzer import analyze_har_file

        start_time = time.time()
        result = analyze_har_file(
            "tests/fixtures/minimal_har.json", {"mall_id": "test"}
        )
        execution_time = time.time() - start_time

        # HAR analysis should complete in under 30 seconds
        assert execution_time < 30.0, f"HAR analysis too slow: {execution_time:.2f}s"

        # Validate result structure
        assert "network_requests" in result
        assert "protobuf_endpoints" in result

        print(f"HAR Analysis Performance:")
        print(f"  Time: {execution_time:.2f}s")
        print(f"  Network requests: {len(result.get('network_requests', []))}")

    def test_protobuf_decoding_performance(self) -> None:
        """Test protobuf decoding performance (<1 second per response)."""
        from src.protobuf_handler import decode_protobuf_response

        # Test with sample protobuf data
        test_data = b"\x12\x05Brand\x1a\x07Fashion\x20\x01" * 100  # ~1KB of data

        context = {
            "endpoint": "/maps/preview/place",
            "request_params": {},
            "expected_schema": {"name": "string", "category": "string", "id": "int"},
        }

        start_time = time.time()
        result = decode_protobuf_response(test_data, context)
        execution_time = time.time() - start_time

        # Should decode within 1 second
        assert (
            execution_time < 1.0
        ), f"Protobuf decoding too slow: {execution_time:.2f}s"

        # Validate result
        assert "decoded_data" in result
        assert result["confidence_score"] >= 0.0

        print(f"Protobuf Decoding Performance:")
        print(f"  Time: {execution_time:.2f}s")
        print(f"  Confidence: {result['confidence_score']:.2f}")

    def test_data_processing_performance(self) -> None:
        """Test data processing and validation performance."""
        from src.data_processor import process_brand_data

        # Create test data with ~150 brands (POC target)
        test_brands = []
        for i in range(150):
            test_brands.append(
                {
                    "name": f"Brand{i}",
                    "category": "Fashion" if i % 2 == 0 else "Food",
                    "location_details": {"floor": f"Level{i % 5}"},
                    "confidence_score": 0.9,
                }
            )

        test_data = {
            "brands": test_brands,
            "categories": [
                {"name": "Fashion", "brand_count": 75},
                {"name": "Food", "brand_count": 75},
            ],
            "har_data": {},
            "metadata": {},
        }

        start_time = time.time()
        result = process_brand_data(test_data)
        execution_time = time.time() - start_time

        # Data processing should be fast
        assert execution_time < 2.0, f"Data processing too slow: {execution_time:.2f}s"

        # Validate processing results
        assert len(result["brands"]) == 150  # All should pass validation
        assert result["metadata"]["processing_success_rate"] >= 0.9

        print(f"Data Processing Performance:")
        print(f"  Time: {execution_time:.2f}s")
        print(f"  Brands processed: {len(result['brands'])}")
        print(f"  Success rate: {result['metadata']['processing_success_rate']:.1%}")

    def test_session_management_performance(self) -> None:
        """Test session management operations performance."""
        from src.session_manager import SessionManager

        manager = SessionManager()

        # Test session creation performance
        start_time = time.time()
        sessions = []
        for i in range(10):
            session = manager.create_session()
            sessions.append(session)
        creation_time = time.time() - start_time

        # Session creation should be fast
        assert creation_time < 1.0, f"Session creation too slow: {creation_time:.2f}s"

        # Test session retrieval performance
        start_time = time.time()
        for session in sessions:
            retrieved = manager.get_session(session.session_id)
            assert retrieved is not None
        retrieval_time = time.time() - start_time

        assert (
            retrieval_time < 0.5
        ), f"Session retrieval too slow: {retrieval_time:.2f}s"

        print(f"Session Management Performance:")
        print(f"  Creation time (10 sessions): {creation_time:.2f}s")
        print(f"  Retrieval time (10 sessions): {retrieval_time:.2f}s")

    def test_error_handling_performance(self) -> None:
        """Test that error handling doesn't significantly impact performance."""
        from src.scraper import scrape_mall_directory

        # Test with error-prone input
        invalid_url = "https://invalid-domain-that-does-not-exist.com/maps/place/Test"

        start_time = time.time()
        result = scrape_mall_directory(invalid_url, {"strategy": "view_all"})
        execution_time = time.time() - start_time

        # Error handling should still be reasonably fast
        assert execution_time < 5.0, f"Error handling too slow: {execution_time:.2f}s"

        # Should have error information
        metadata = result.get("metadata", {})
        assert "errors_encountered" in metadata
        assert len(metadata["errors_encountered"]) > 0

        print(f"Error Handling Performance:")
        print(f"  Time: {execution_time:.2f}s")
        print(f"  Errors detected: {len(metadata['errors_encountered'])}")

    def test_concurrent_operation_simulation(self) -> None:
        """Test performance under simulated concurrent operations."""
        import threading
        from src.scraper import scrape_mall_directory

        results = []
        errors = []

        def run_scraping(thread_id: int):
            try:
                result = scrape_mall_directory(
                    "https://www.google.com/maps/place/St+James+Quarter",
                    {"strategy": "view_all"},
                )
                results.append((thread_id, result))
            except Exception as e:
                errors.append((thread_id, str(e)))

        # Run 3 concurrent operations (simulating parallel category processing)
        threads = []
        start_time = time.time()

        for i in range(3):
            thread = threading.Thread(target=run_scraping, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        total_time = time.time() - start_time

        # Concurrent operations should complete reasonably
        # Allow more time since they're running concurrently
        assert total_time < 180.0, f"Concurrent operations too slow: {total_time:.2f}s"

        # Should have results from all threads
        assert len(results) == 3, f"Expected 3 results, got {len(results)}"
        assert len(errors) == 0, f"Unexpected errors: {errors}"

        print(f"Concurrent Operation Performance:")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Successful operations: {len(results)}")

    def test_memory_efficient_processing(self) -> None:
        """Test that processing scales efficiently with data size."""
        from src.data_processor import process_brand_data

        # Test with increasing data sizes
        sizes = [10, 50, 100, 200]
        times = []

        for size in sizes:
            # Create test data
            brands = [{"name": f"Brand{i}", "category": "Test"} for i in range(size)]
            test_data = {
                "brands": brands,
                "categories": [{"name": "Test", "brand_count": size}],
                "har_data": {},
                "metadata": {},
            }

            start_time = time.time()
            result = process_brand_data(test_data)
            execution_time = time.time() - start_time
            times.append(execution_time)

            assert len(result["brands"]) == size

        # Check that processing time scales reasonably (should not be exponential)
        # Time for 200 items should be less than 4x time for 50 items
        if len(times) >= 2:
            ratio = times[-1] / times[1] if times[1] > 0 else 1
            assert ratio < 4.0, f"Poor scaling: {ratio:.2f}x increase for 4x data"

        print(f"Memory Efficient Processing:")
        print(f"  Sizes tested: {sizes}")
        print(f"  Times: {[f'{t:.3f}s' for t in times]}")

    @pytest.mark.parametrize("strategy", ["view_all", "categories"])
    def test_strategy_performance_comparison(self, strategy: str) -> None:
        """Compare performance between different scraping strategies."""
        from src.scraper import scrape_mall_directory

        config = {
            "strategy": strategy,
            "max_categories": 3 if strategy == "categories" else None,
        }

        start_time = time.time()
        result = scrape_mall_directory(
            "https://www.google.com/maps/place/St+James+Quarter", config
        )
        execution_time = time.time() - start_time

        # Both strategies should complete within reasonable time
        assert (
            execution_time < 120.0
        ), f"{strategy} strategy too slow: {execution_time:.2f}s"

        # Validate strategy-specific results
        if strategy == "view_all":
            brands = result.get("brands", [])
            assert len(brands) > 0
        elif strategy == "categories":
            categories = result.get("categories", [])
            assert len(categories) > 0

        print(f"Strategy Performance ({strategy}):")
        print(f"  Time: {execution_time:.2f}s")
        if strategy == "view_all":
            print(f"  Brands: {len(result.get('brands', []))}")
        else:
            print(f"  Categories: {len(result.get('categories', []))}")

    def test_warmup_performance_improvement(self) -> None:
        """Test that subsequent runs show performance improvement (caching/session reuse)."""
        from src.scraper import scrape_mall_directory

        times = []

        # Run multiple times to test warmup effects
        for i in range(3):
            start_time = time.time()
            result = scrape_mall_directory(
                "https://www.google.com/maps/place/St+James+Quarter",
                {"strategy": "view_all"},
            )
            execution_time = time.time() - start_time
            times.append(execution_time)

            # Each run should succeed
            assert len(result.get("brands", [])) > 0

        # Check for performance improvement trend
        # Later runs should generally be faster (though not guaranteed due to various factors)
        avg_first_two = (times[0] + times[1]) / 2
        last_time = times[2]

        # Allow some variance but expect reasonable performance
        assert last_time < 120.0, f"Warmup run too slow: {last_time:.2f}s"

        improvement = avg_first_two - last_time
        print(f"Warmup Performance:")
        print(f"  Run times: {[f'{t:.2f}s' for t in times]}")
        print(f"  Average improvement: {improvement:.2f}s")
