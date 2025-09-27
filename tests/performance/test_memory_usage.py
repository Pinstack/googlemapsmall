"""Performance tests for memory usage validation.

Tests ensure the Google Maps Mall Scraper stays under 500MB memory usage
during operation. Monitors memory consumption across different operations.
"""

import gc
import psutil
import pytest
from typing import Any, Dict, List


class TestMemoryUsage:
    """Test cases for memory usage performance requirements."""

    def test_end_to_end_scraping_memory_under_500mb(self) -> None:
        """Test complete mall scraping stays under 500MB memory usage."""
        import os
        from src.scraper import scrape_mall_directory

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        mall_url = "https://www.google.com/maps/place/St+James+Quarter"
        strategy_config = {"strategy": "view_all", "max_brands": 150}

        # Execute complete scraping workflow
        result = scrape_mall_directory(mall_url, strategy_config)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = final_memory - initial_memory

        # Validate memory requirement
        assert (
            memory_used < 500.0
        ), f"Memory usage {memory_used:.1f}MB exceeds 500MB limit"

        # Force garbage collection and check again
        gc.collect()
        after_gc_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_after_gc = after_gc_memory - initial_memory

        assert (
            memory_after_gc < 500.0
        ), f"Memory after GC {memory_after_gc:.1f}MB exceeds 500MB limit"

        # Validate result quality
        assert "brands" in result
        assert len(result["brands"]) > 0

        print(f"End-to-End Memory Test:")
        print(f"  Initial memory: {initial_memory:.1f}MB")
        print(f"  Final memory: {final_memory:.1f}MB")
        print(f"  Memory used: {memory_used:.1f}MB")
        print(f"  After GC: {memory_after_gc:.1f}MB")

    def test_har_analysis_memory_usage(self) -> None:
        """Test HAR file analysis memory usage."""
        import os
        from src.har_analyzer import analyze_har_file

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Analyze HAR file
        result = analyze_har_file(
            "tests/fixtures/minimal_har.json", {"mall_id": "test"}
        )

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = final_memory - initial_memory

        # HAR analysis should use reasonable memory
        assert memory_used < 100.0, f"HAR analysis memory {memory_used:.1f}MB too high"

        # Validate result
        assert "network_requests" in result

        print(f"HAR Analysis Memory:")
        print(f"  Memory used: {memory_used:.1f}MB")

    def test_protobuf_processing_memory_usage(self) -> None:
        """Test protobuf decoding memory usage."""
        import os
        from src.protobuf_handler import decode_protobuf_response

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Test with various protobuf sizes
        test_sizes = [1, 10, 100]  # KB

        for size_kb in test_sizes:
            # Create test data of specified size
            test_data = b"\x12\x05Brand\x1a\x07Fashion" * (
                size_kb * 1024 // 12
            )  # Approximate

            context = {
                "endpoint": "/maps/preview/place",
                "request_params": {},
                "expected_schema": {"name": "string", "category": "string"},
            }

            before_decode = process.memory_info().rss / 1024 / 1024  # MB
            result = decode_protobuf_response(test_data, context)
            after_decode = process.memory_info().rss / 1024 / 1024  # MB

            memory_for_decode = after_decode - before_decode

            # Each decode should use reasonable memory
            assert (
                memory_for_decode < 50.0
            ), f"Protobuf decode memory {memory_for_decode:.1f}MB too high for {size_kb}KB input"

            # Validate result
            assert "decoded_data" in result

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_memory_used = final_memory - initial_memory

        print(f"Protobuf Processing Memory:")
        print(f"  Total memory used: {total_memory_used:.1f}MB")

    def test_data_processing_memory_usage(self) -> None:
        """Test data processing memory usage with large datasets."""
        import os
        from src.data_processor import process_brand_data

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Test with increasing data sizes
        sizes = [50, 100, 200]

        for size in sizes:
            # Create test data
            brands = []
            for i in range(size):
                brands.append(
                    {
                        "name": f"Brand{i}",
                        "category": "Fashion" if i % 2 == 0 else "Food",
                        "location_details": {
                            "floor": f"Level{i % 5}",
                            "unit": f"Unit{i}",
                        },
                        "confidence_score": 0.9,
                        "phone": f"+44{i:010d}",
                        "website": f"https://brand{i}.com",
                        "rating": 4.5,
                        "review_count": 100 + i,
                    }
                )

            test_data = {
                "brands": brands,
                "categories": [
                    {"name": "Fashion", "brand_count": size // 2},
                    {"name": "Food", "brand_count": size // 2},
                ],
                "har_data": {"large_data": "x" * 100000},  # 100KB HAR data
                "metadata": {},
            }

            before_process = process.memory_info().rss / 1024 / 1024  # MB
            result = process_brand_data(test_data)
            after_process = process.memory_info().rss / 1024 / 1024  # MB

            memory_for_processing = after_process - before_process

            # Processing should use reasonable memory
            assert (
                memory_for_processing < 100.0
            ), f"Data processing memory {memory_for_processing:.1f}MB too high for {size} brands"

            # Validate results
            assert len(result["brands"]) == size
            assert result["metadata"]["processing_success_rate"] >= 0.9

            # Clean up to prevent memory accumulation in test
            del result
            gc.collect()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_memory_used = final_memory - initial_memory

        print(f"Data Processing Memory:")
        print(f"  Total memory used: {total_memory_used:.1f}MB")

    def test_session_management_memory_usage(self) -> None:
        """Test session management memory usage."""
        import os
        from src.session_manager import SessionManager

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        manager = SessionManager()

        # Create multiple sessions
        sessions_created = 0
        for i in range(10):
            session = manager.create_session()
            # Add some realistic session data
            session.set_cookie(f"cookie{i}", f"value{i}")
            session.set_auth_token(f"token{i}", f"token_value_{i}")
            sessions_created += 1

        after_sessions = process.memory_info().rss / 1024 / 1024  # MB
        memory_for_sessions = after_sessions - initial_memory

        # Session management should use reasonable memory
        assert (
            memory_for_sessions < 50.0
        ), f"Session memory {memory_for_sessions:.1f}MB too high for {sessions_created} sessions"

        # Test cleanup
        manager.cleanup_expired_sessions()
        after_cleanup = process.memory_info().rss / 1024 / 1024  # MB

        print(f"Session Management Memory:")
        print(f"  Memory for sessions: {memory_for_sessions:.1f}MB")
        print(f"  After cleanup: {after_cleanup - initial_memory:.1f}MB")

    def test_concurrent_operation_memory_usage(self) -> None:
        """Test memory usage during concurrent operations."""
        import os
        import threading
        from src.scraper import scrape_mall_directory

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        results = []
        peak_memory = initial_memory

        def run_scraping(thread_id: int):
            nonlocal peak_memory
            try:
                result = scrape_mall_directory(
                    "https://www.google.com/maps/place/St+James+Quarter",
                    {"strategy": "view_all"},
                )
                results.append((thread_id, result))

                # Track peak memory usage
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                peak_memory = max(peak_memory, current_memory)

            except Exception as e:
                results.append((thread_id, f"error: {e}"))

        # Run concurrent operations
        threads = []
        for i in range(3):
            thread = threading.Thread(target=run_scraping, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = final_memory - initial_memory
        peak_usage = peak_memory - initial_memory

        # Concurrent operations should stay within memory limits
        assert (
            memory_used < 500.0
        ), f"Concurrent memory usage {memory_used:.1f}MB exceeds 500MB limit"
        assert (
            peak_usage < 500.0
        ), f"Peak memory usage {peak_usage:.1f}MB exceeds 500MB limit"

        # Should have results from all threads
        successful_results = [
            r
            for r in results
            if not isinstance(r[1], str) or not r[1].startswith("error")
        ]
        assert (
            len(successful_results) == 3
        ), f"Expected 3 successful results, got {len(successful_results)}"

        print(f"Concurrent Operation Memory:")
        print(f"  Final memory used: {memory_used:.1f}MB")
        print(f"  Peak memory used: {peak_usage:.1f}MB")
        print(f"  Successful operations: {len(successful_results)}")

    def test_memory_leak_detection(self) -> None:
        """Test for memory leaks during repeated operations."""
        import os
        from src.scraper import scrape_mall_directory

        process = psutil.Process(os.getpid())

        # Run multiple scraping operations
        memory_readings = []

        for i in range(5):
            result = scrape_mall_directory(
                "https://www.google.com/maps/place/St+James+Quarter",
                {"strategy": "view_all"},
            )

            # Force garbage collection
            gc.collect()

            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_readings.append(current_memory)

            # Each operation should succeed
            assert len(result.get("brands", [])) > 0

        # Check for significant memory growth (potential leak)
        if len(memory_readings) >= 2:
            initial_memory = memory_readings[0]
            final_memory = memory_readings[-1]
            memory_growth = final_memory - initial_memory

            # Allow some growth but not excessive (max 50MB growth for 5 operations)
            assert (
                memory_growth < 50.0
            ), f"Potential memory leak: {memory_growth:.1f}MB growth over {len(memory_readings)} operations"

        print(f"Memory Leak Detection:")
        print(f"  Memory readings: {[f'{m:.1f}MB' for m in memory_readings]}")
        if len(memory_readings) >= 2:
            growth = memory_readings[-1] - memory_readings[0]
            print(f"  Total growth: {growth:.1f}MB")

    def test_large_har_file_memory_handling(self) -> None:
        """Test memory handling with simulated large HAR files."""
        import os
        import tempfile
        import json
        from src.har_analyzer import analyze_har_file

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create a simulated large HAR file
        large_har_data = {
            "log": {
                "version": "1.2",
                "creator": {"name": "Test", "version": "1.0"},
                "entries": [],
            }
        }

        # Add many entries (simulate 40MB HAR file)
        for i in range(1000):
            large_har_data["log"]["entries"].append(
                {
                    "request": {
                        "method": "GET",
                        "url": f"https://maps.google.com/endpoint{i}",
                    },
                    "response": {
                        "status": 200,
                        "content": {
                            "size": 40000,
                            "text": "x" * 40000,
                        },  # 40KB per response
                    },
                }
            )

        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(large_har_data, f)
            temp_file = f.name

        try:
            before_analysis = process.memory_info().rss / 1024 / 1024  # MB
            result = analyze_har_file(temp_file, {"mall_id": "test"})
            after_analysis = process.memory_info().rss / 1024 / 1024  # MB

            memory_for_analysis = after_analysis - before_analysis

            # Large HAR analysis should use reasonable memory
            assert (
                memory_for_analysis < 200.0
            ), f"Large HAR analysis memory {memory_for_analysis:.1f}MB too high"

            # Should process the data
            assert "network_requests" in result
            assert len(result["network_requests"]) > 0

        finally:
            # Clean up temp file
            os.unlink(temp_file)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_memory_used = final_memory - initial_memory

        print(f"Large HAR File Memory:")
        print(f"  Memory for analysis: {memory_for_analysis:.1f}MB")
        print(f"  Total memory used: {total_memory_used:.1f}MB")

    def test_memory_cleanup_after_operations(self) -> None:
        """Test that memory is properly cleaned up after operations."""
        import os
        from src.scraper import scrape_mall_directory
        from src.data_processor import process_brand_data

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Run a series of operations
        operations = []

        # Operation 1: Scraping
        result1 = scrape_mall_directory(
            "https://www.google.com/maps/place/St+James+Quarter",
            {"strategy": "view_all"},
        )
        operations.append(("scraping", process.memory_info().rss / 1024 / 1024))

        # Operation 2: Data processing
        result2 = process_brand_data(result1)
        operations.append(("processing", process.memory_info().rss / 1024 / 1024))

        # Operation 3: More scraping
        result3 = scrape_mall_directory(
            "https://www.google.com/maps/place/St+James+Quarter",
            {"strategy": "categories", "max_categories": 3},
        )
        operations.append(("more_scraping", process.memory_info().rss / 1024 / 1024))

        # Delete references and force cleanup
        del result1, result2, result3
        gc.collect()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = final_memory - initial_memory

        # Overall memory usage should be reasonable
        assert (
            memory_used < 500.0
        ), f"Overall memory usage {memory_used:.1f}MB exceeds 500MB limit"

        print(f"Memory Cleanup Test:")
        print(f"  Initial memory: {initial_memory:.1f}MB")
        print(
            f"  Peak operations memory: {[f'{op[0]}: {op[1]:.1f}MB' for op in operations]}"
        )
        print(f"  Final memory: {final_memory:.1f}MB")
        print(f"  Net usage: {memory_used:.1f}MB")

    @pytest.mark.parametrize("data_size", [10, 50, 100])
    def test_memory_scaling_with_data_size(self, data_size: int) -> None:
        """Test how memory usage scales with data size."""
        import os
        from src.data_processor import process_brand_data

        process = psutil.Process(os.getpid())

        # Create test data of specified size
        brands = []
        for i in range(data_size):
            brands.append(
                {
                    "name": f"Brand{i}",
                    "category": "Test",
                    "location_details": {"floor": f"Level{i % 10}"},
                    "confidence_score": 0.9,
                }
            )

        test_data = {
            "brands": brands,
            "categories": [{"name": "Test", "brand_count": data_size}],
            "har_data": {},
            "metadata": {},
        }

        before_process = process.memory_info().rss / 1024 / 1024  # MB
        result = process_brand_data(test_data)
        after_process = process.memory_info().rss / 1024 / 1024  # MB

        memory_used = after_process - before_process

        # Memory usage should scale reasonably with data size
        # Allow up to 10MB per 100 items
        max_expected_memory = (data_size / 100) * 10
        assert (
            memory_used < max_expected_memory
        ), f"Memory usage {memory_used:.1f}MB too high for {data_size} items"

        # Validate result
        assert len(result["brands"]) == data_size

        print(f"Memory Scaling Test ({data_size} items):")
        print(f"  Memory used: {memory_used:.1f}MB")
        print(f"  Per item: {memory_used / data_size:.3f}MB")
