"""Pytest configuration and shared fixtures for Google Maps Mall Scraper."""

import json
from pathlib import Path
from typing import Any, Dict, cast

import pytest


@pytest.fixture  # type: ignore[misc]
def fixtures_dir() -> Path:
    """Path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture  # type: ignore[misc]
def minimal_har_data(fixtures_dir: Path) -> Dict[str, Any]:
    """Load minimal HAR test data."""
    with open(fixtures_dir / "minimal_har.json", "r", encoding="utf-8") as f:
        return cast(Dict[str, Any], json.load(f))


@pytest.fixture  # type: ignore[misc]
def sample_protobuf_schema(fixtures_dir: Path) -> Dict[str, Any]:
    """Load sample protobuf schema."""
    schema_path = fixtures_dir / "sample_protobuf_schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        return cast(Dict[str, Any], json.load(f))


@pytest.fixture  # type: ignore[misc]
def sample_decoded_protobuf(fixtures_dir: Path) -> Dict[str, Any]:
    """Load sample decoded protobuf data."""
    with open(
        fixtures_dir / "sample_decoded_protobuf.json", "r", encoding="utf-8"
    ) as f:
        return cast(Dict[str, Any], json.load(f))


@pytest.fixture  # type: ignore[misc]
def mall_context() -> Dict[str, Any]:
    """Sample mall context for testing."""
    return {
        "mall_id": "0x4887c78e6281b45d:0xc4ad4b61a12fde3f",
        "name": "St James Quarter",
        "coordinates": [55.9552777, -3.1885505],
        "expected_brand_count": 150,
    }


@pytest.fixture  # type: ignore[misc]
def mock_protobuf_bytes() -> bytes:
    """Mock protobuf bytes for testing."""
    # This is a minimal protobuf message (just for testing)
    return b"\x12\x05Hello\x18\x01"


@pytest.fixture  # type: ignore[misc]
def mock_network_request() -> Dict[str, Any]:
    """Mock network request data."""
    return {
        "url": "https://www.google.com/maps/preview/place?pb=test",
        "method": "GET",
        "headers": {"User-Agent": "Test/1.0"},
        "response_status": 200,
        "response_size": 12345,
        "is_protobuf": False,
    }
