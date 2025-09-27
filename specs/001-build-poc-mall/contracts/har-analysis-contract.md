# Contract: HAR Analysis Module

**Contract ID**: HAR-ANALYSIS-001
**Version**: 1.0
**Date**: 2025-09-27

## Overview
The HAR Analysis Module processes captured HTTP Archive (HAR) files to extract Google Maps network patterns and identify tenant data loading mechanisms.

## Interface Definition

### Input
```python
def analyze_har_file(har_file_path: str, mall_context: dict) -> dict:
    """
    Analyze HAR file for Google Maps mall interactions.

    Args:
        har_file_path: Path to HAR file
        mall_context: Dict with mall_id, coordinates, expected_brand_count

    Returns:
        Dict containing:
        - network_requests: List of identified API calls
        - protobuf_endpoints: List of protobuf-encoded endpoints
        - data_patterns: Identified loading patterns
        - session_context: Extracted session parameters
    """
```

### Output Schema
```json
{
  "network_requests": [
    {
      "url": "string",
      "method": "GET|POST",
      "protobuf_params": "string",
      "response_size": "integer",
      "is_tenant_data": "boolean",
      "category": "view_all|category_pagination|tile_data"
    }
  ],
  "protobuf_endpoints": [
    {
      "endpoint": "string",
      "parameter_structure": "object",
      "response_schema": "object",
      "frequency": "integer"
    }
  ],
  "data_patterns": {
    "pagination_trigger": "string",
    "session_persistence": "object",
    "rate_limiting": "object"
  },
  "session_context": {
    "auth_params": "object",
    "client_fingerprint": "string",
    "session_id": "string"
  }
}
```

## Contract Tests

### Test Case 1: HAR File Loading
```python
def test_har_file_loading():
    result = analyze_har_file("googlemaps.har", {"mall_id": "test"})
    assert result is not None
    assert "network_requests" in result
    assert len(result["network_requests"]) > 0
```

### Test Case 2: Protobuf Endpoint Detection
```python
def test_protobuf_endpoint_detection():
    result = analyze_har_file("googlemaps.har", {"mall_id": "test"})
    protobuf_endpoints = result.get("protobuf_endpoints", [])
    assert any("pb=" in endpoint["endpoint"] for endpoint in protobuf_endpoints)
```

### Test Case 3: Data Pattern Recognition
```python
def test_data_pattern_recognition():
    result = analyze_har_file("googlemaps.har", {"mall_id": "test"})
    patterns = result.get("data_patterns", {})
    assert "pagination_trigger" in patterns
    assert "session_persistence" in patterns
```

## Error Handling
- **FileNotFoundError**: When HAR file doesn't exist
- **InvalidHarFormat**: When HAR file is malformed
- **EmptyHarData**: When HAR contains no relevant requests
- **ProtobufDecodeError**: When protobuf parameters cannot be parsed

## Performance Requirements
- HAR file processing: <30 seconds for 40MB file
- Memory usage: <500MB during processing
- Thread safety: Must be stateless for parallel processing
