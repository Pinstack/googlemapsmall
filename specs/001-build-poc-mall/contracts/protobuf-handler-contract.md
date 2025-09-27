# Contract: Protobuf Handler Module

**Contract ID**: PROTOBUF-HANDLER-001
**Version**: 1.0
**Date**: 2025-09-27

## Overview
The Protobuf Handler Module decodes Google Maps protobuf-encoded data and reconstructs parameters for API calls. Uses blackboxprotobuf for schema inference and parameter reconstruction.

## Interface Definition

### Input
```python
def decode_protobuf_response(raw_bytes: bytes, context: dict) -> dict:
    """
    Decode protobuf response into structured data.

    Args:
        raw_bytes: Raw protobuf bytes from network response
        context: Context dict with endpoint, request_params, expected_schema

    Returns:
        Dict containing:
        - decoded_data: Structured JSON representation
        - schema_info: Inferred protobuf schema
        - field_mappings: Field name to protobuf tag mappings
        - confidence_score: Schema inference confidence (0.0-1.0)
    """

def reconstruct_protobuf_params(template_params: dict, context: dict) -> str:
    """
    Reconstruct protobuf parameters for API calls.

    Args:
        template_params: Parameter template from HAR analysis
        context: Context with session data, coordinates, etc.

    Returns:
        Encoded protobuf parameter string for URL inclusion
    """
```

### Output Schemas

#### Decode Response Schema
```json
{
  "decoded_data": {
    "tenant_list": [
      {
        "name": "string",
        "category": "string",
        "location": "object"
      }
    ],
    "pagination_info": {
      "has_more": "boolean",
      "next_token": "string"
    }
  },
  "schema_info": {
    "field_count": "integer",
    "nested_messages": "array",
    "repeated_fields": "array"
  },
  "field_mappings": {
    "1": "tenant_list",
    "2": "pagination_info"
  },
  "confidence_score": 0.85
}
```

#### Parameter Reconstruction Schema
```json
{
  "encoded_params": "!1m16!1sPLACE_ID!3m8!1m3!1dDELTA!2dLONG!3dLAT...",
  "parameter_map": {
    "place_id": "PLACE_ID",
    "coordinates": "LAT,LONG",
    "viewport": "WIDTH,HEIGHT"
  },
  "validation_status": "valid|warning|error"
}
```

## Contract Tests

### Test Case 1: Protobuf Decoding
```python
def test_protobuf_decoding():
    raw_data = b"\x12\x05Hello"  # Sample protobuf
    result = decode_protobuf_response(raw_data, {"endpoint": "/maps/preview/place"})

    assert result["decoded_data"] is not None
    assert "confidence_score" in result
    assert result["confidence_score"] > 0.0
```

### Test Case 2: Parameter Reconstruction
```python
def test_parameter_reconstruction():
    template = {"place_id": "test_id", "coordinates": [55.95, -3.18]}
    result = reconstruct_protobuf_params(template, {"session_id": "abc123"})

    assert "pb=" in result["encoded_params"]
    assert result["validation_status"] == "valid"
    assert "parameter_map" in result
```

### Test Case 3: Schema Evolution Handling
```python
def test_schema_evolution():
    # Test with slightly different protobuf structure
    result = decode_protobuf_response(modified_bytes, {"endpoint": "/maps/preview/place"})

    assert result["confidence_score"] >= 0.7  # Should handle minor schema changes
    assert result["decoded_data"] is not None
```

## Error Handling
- **ProtobufDecodeError**: When protobuf cannot be decoded
- **SchemaInferenceError**: When schema cannot be inferred with sufficient confidence
- **ParameterReconstructionError**: When required parameters are missing
- **SchemaDriftWarning**: When schema appears to have changed significantly

## Performance Requirements
- Protobuf decoding: <1 second for 1MB response
- Parameter reconstruction: <100ms per request
- Schema inference: <5 seconds for new schema types
- Memory usage: <100MB for schema cache

## Schema Evolution Handling
- Confidence scoring for schema inference reliability
- Fallback to previous known schemas
- Warning system for significant schema changes
- Version tracking for protobuf schema evolution
