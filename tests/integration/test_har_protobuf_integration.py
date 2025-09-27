"""Integration tests for HAR analyzer and protobuf handler integration.

Tests the combined functionality of HAR analysis and protobuf parameter reconstruction.
These tests MUST FAIL initially (no integration yet) - TDD approach.
"""

import pytest
from pathlib import Path
from typing import Any, Dict


class TestHarProtobufIntegration:
    """Test cases for HAR analyzer and protobuf handler integration."""

    def test_extract_and_reconstruct_protobuf_params(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test extracting protobuf parameters from HAR and reconstructing them."""
        # This test will fail until integration is implemented
        from src.har_analyzer import analyze_har_file
        from src.protobuf_handler import reconstruct_protobuf_params

        # Create mall context
        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        # Analyze HAR file
        har_results = analyze_har_file("tests/fixtures/minimal_har.json", mall_context)

        # Extract protobuf endpoints
        protobuf_endpoints = har_results.get("protobuf_endpoints", [])
        assert len(protobuf_endpoints) > 0, "No protobuf endpoints found in HAR"

        # Get first protobuf endpoint
        endpoint = protobuf_endpoints[0]
        pb_params = endpoint.get("parameter_structure")

        # Reconstruct protobuf parameters
        if pb_params:
            template = {"place_id": "ChIJabcd1234", "coordinates": [55.95, -3.18]}
            context = {"session_id": "test_session_123"}

            reconstructed = reconstruct_protobuf_params(template, context)

            # Verify reconstruction
            assert "encoded_params" in reconstructed
            assert "parameter_map" in reconstructed
            assert reconstructed["validation_status"] == "valid"

            # Encoded params should contain the expected format
            encoded = reconstructed["encoded_params"]
            assert isinstance(encoded, str)
            assert len(encoded) > 0

    def test_har_analysis_provides_protobuf_context(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test that HAR analysis provides context needed for protobuf reconstruction."""
        # This test will fail until integration is implemented
        from src.har_analyzer import analyze_har_file

        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        har_results = analyze_har_file("tests/fixtures/minimal_har.json", mall_context)

        # Check that HAR analysis provides session context
        session_context = har_results.get("session_context", {})
        assert isinstance(session_context, dict)

        # Should have some form of session identification
        has_session_info = (
            session_context.get("session_id")
            or session_context.get("auth_params")
            or session_context.get("client_fingerprint")
        )
        assert (
            has_session_info
        ), "HAR analysis should extract session context for protobuf reconstruction"

    def test_protobuf_parameter_workflow(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test complete workflow from HAR extraction to protobuf reconstruction."""
        # This test will fail until integration is implemented
        from src.har_analyzer import analyze_har_file
        from src.protobuf_handler import reconstruct_protobuf_params

        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        # Step 1: Analyze HAR to extract patterns
        har_results = analyze_har_file("tests/fixtures/minimal_har.json", mall_context)

        # Step 2: Extract data patterns for pagination/session handling
        data_patterns = har_results.get("data_patterns", {})
        assert "pagination_trigger" in data_patterns
        assert "session_persistence" in data_patterns

        # Step 3: Use session context for protobuf reconstruction
        session_context = har_results.get("session_context", {})

        # Step 4: Reconstruct parameters with session context
        template = {"place_id": "ChIJabcd1234", "coordinates": [55.95, -3.18]}
        context = {"session_id": session_context.get("session_id", "default_session")}

        reconstructed = reconstruct_protobuf_params(template, context)

        # Verify the complete workflow
        assert reconstructed["validation_status"] == "valid"
        assert (
            "pb=" in reconstructed["encoded_params"]
            or "!" in reconstructed["encoded_params"]
        )

    def test_multiple_protobuf_endpoints_handling(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test handling multiple protobuf endpoints from HAR analysis."""
        # This test will fail until integration is implemented
        from src.har_analyzer import analyze_har_file
        from src.protobuf_handler import reconstruct_protobuf_params

        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        har_results = analyze_har_file("tests/fixtures/minimal_har.json", mall_context)
        protobuf_endpoints = har_results.get("protobuf_endpoints", [])

        if len(protobuf_endpoints) > 1:
            # Test reconstructing parameters for different endpoints
            context = {"session_id": "test_session_123"}

            for endpoint in protobuf_endpoints[:2]:  # Test first 2 endpoints
                template = {"place_id": "ChIJabcd1234", "coordinates": [55.95, -3.18]}

                reconstructed = reconstruct_protobuf_params(template, context)
                assert reconstructed["validation_status"] == "valid"
                assert isinstance(reconstructed["encoded_params"], str)

    def test_har_protobuf_error_handling(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test error handling in HAR analysis to protobuf reconstruction workflow."""
        # This test will fail until integration is implemented
        from src.har_analyzer import analyze_har_file
        from src.protobuf_handler import reconstruct_protobuf_params

        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        # Test with valid HAR analysis
        har_results = analyze_har_file("tests/fixtures/minimal_har.json", mall_context)

        # Test protobuf reconstruction with missing required parameters
        incomplete_template = {"place_id": "ChIJabcd1234"}  # Missing coordinates

        with pytest.raises((ValueError, KeyError)):
            reconstruct_protobuf_params(incomplete_template, {"session_id": "test"})

        # Test protobuf reconstruction with invalid coordinates
        invalid_template = {
            "place_id": "ChIJabcd1234",
            "coordinates": "invalid_coords",  # Should be list
        }

        with pytest.raises((ValueError, TypeError)):
            reconstruct_protobuf_params(invalid_template, {"session_id": "test"})

    def test_session_context_integration(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test that session context from HAR analysis integrates with protobuf reconstruction."""
        # This test will fail until integration is implemented
        from src.har_analyzer import analyze_har_file
        from src.protobuf_handler import reconstruct_protobuf_params

        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        # Get session context from HAR analysis
        har_results = analyze_har_file("tests/fixtures/minimal_har.json", mall_context)
        session_context = har_results.get("session_context", {})

        # Use session context in protobuf reconstruction
        template = {"place_id": "ChIJabcd1234", "coordinates": [55.95, -3.18]}

        # Test with extracted session context
        context_with_session = {
            "session_id": session_context.get("session_id", "extracted_session")
        }
        reconstructed_with_session = reconstruct_protobuf_params(
            template, context_with_session
        )

        # Test with default context
        context_default = {"session_id": "default_session"}
        reconstructed_default = reconstruct_protobuf_params(template, context_default)

        # Both should be valid
        assert reconstructed_with_session["validation_status"] == "valid"
        assert reconstructed_default["validation_status"] == "valid"

        # Results should be similar (same template, different session)
        assert (
            reconstructed_with_session["encoded_params"]
            != reconstructed_default["encoded_params"]
        )

    def test_network_patterns_influence_protobuf_structure(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test that network patterns from HAR analysis influence protobuf structure."""
        # This test will fail until integration is implemented
        from src.har_analyzer import analyze_har_file

        mall_context = {
            "mall_id": "ChIJabcd1234",
            "name": "Test Mall",
            "coordinates": [55.95, -3.18],
            "expected_brand_count": 150,
        }

        har_results = analyze_har_file("tests/fixtures/minimal_har.json", mall_context)

        # Check that data patterns include pagination and session info
        data_patterns = har_results.get("data_patterns", {})
        assert isinstance(data_patterns, dict)

        # These patterns should help determine protobuf structure
        expected_patterns = [
            "pagination_trigger",
            "session_persistence",
            "rate_limiting",
        ]
        for pattern in expected_patterns:
            assert pattern in data_patterns, f"Missing expected pattern: {pattern}"

        # Session persistence should indicate how to handle auth in protobuf
        session_persistence = data_patterns.get("session_persistence", {})
        assert isinstance(session_persistence, dict)

    def test_protobuf_parameter_consistency(
        self, minimal_har_data: Dict[str, Any]
    ) -> None:
        """Test that reconstructed protobuf parameters are consistent across calls."""
        # This test will fail until integration is implemented
        from src.protobuf_handler import reconstruct_protobuf_params

        template = {"place_id": "ChIJabcd1234", "coordinates": [55.95, -3.18]}
        context = {"session_id": "test_session_123"}

        # Reconstruct multiple times
        results = []
        for _ in range(3):
            result = reconstruct_protobuf_params(template, context)
            results.append(result)

        # All results should be identical (deterministic)
        first_result = results[0]
        for result in results[1:]:
            assert result["encoded_params"] == first_result["encoded_params"]
            assert result["parameter_map"] == first_result["parameter_map"]
            assert result["validation_status"] == first_result["validation_status"]
