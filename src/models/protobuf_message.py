"""ProtobufMessage dataclass for decoded protobuf structures.

Represents decoded protobuf structures from network responses.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Union
import hashlib


@dataclass
class ProtobufMessage:
    """Represents a decoded protobuf message from Google Maps responses.

    Attributes:
        id: Unique message identifier
        schema_hash: Hash of inferred protobuf schema
        field_count: Number of top-level fields
        decoded_data: Structured JSON representation
        raw_bytes: Original protobuf bytes for debugging
        source_request_id: Reference to originating NetworkRequest
        confidence_score: Schema inference confidence (0.0-1.0)
        decode_time: Time taken to decode (seconds)
    """
    id: Optional[str] = None
    schema_hash: str = ""
    field_count: int = 0
    decoded_data: Dict[str, Any] = field(default_factory=dict)
    raw_bytes: Optional[bytes] = None
    source_request_id: Optional[str] = None
    confidence_score: float = 0.0
    decode_time: float = 0.0

    def __post_init__(self):
        """Validate and compute derived fields after initialization."""
        self._validate_fields()
        self._compute_schema_hash()

    def _validate_fields(self):
        """Validate all fields."""
        if self.confidence_score < 0.0 or self.confidence_score > 1.0:
            raise ValueError(f"Confidence score must be 0.0-1.0, got {self.confidence_score}")

        if self.decode_time < 0.0:
            raise ValueError(f"Decode time must be non-negative, got {self.decode_time}")

        if self.field_count < 0:
            raise ValueError(f"Field count must be non-negative, got {self.field_count}")

        if not isinstance(self.decoded_data, dict):
            raise ValueError("Decoded data must be a dictionary")

        # Validate schema hash format if present
        if self.schema_hash and not self.schema_hash.replace("-", "").isalnum():
            raise ValueError(f"Invalid schema hash format: {self.schema_hash}")

    def _compute_schema_hash(self):
        """Compute schema hash from decoded data structure."""
        if not self.schema_hash and self.decoded_data:
            # Create a hash based on the structure of decoded_data
            structure_str = self._get_structure_string(self.decoded_data)
            self.schema_hash = hashlib.md5(structure_str.encode()).hexdigest()[:16]

    def _get_structure_string(self, data: Any, path: str = "") -> str:
        """Generate a string representing the structure of the data."""
        if isinstance(data, dict):
            keys = sorted(data.keys())
            return f"dict({','.join(f'{k}:{self._get_structure_string(data[k], f'{path}.{k}')}' for k in keys)})"
        elif isinstance(data, list):
            if data:
                return f"list[{self._get_structure_string(data[0], f'{path}[]')}]"
            else:
                return "list[]"
        elif isinstance(data, str):
            return "str"
        elif isinstance(data, (int, float)):
            return "num"
        elif isinstance(data, bool):
            return "bool"
        else:
            return "unknown"

    def has_tenant_data(self) -> bool:
        """Check if this message contains tenant/brand data."""
        if not self.decoded_data:
            return False

        # Look for common tenant data patterns
        tenant_indicators = [
            "tenant_list",
            "brand_list",
            "store_list",
            "business_list",
            "place_list"
        ]

        data_str = str(self.decoded_data).lower()
        return any(indicator in data_str for indicator in tenant_indicators)

    def extract_tenant_data(self) -> Dict[str, Any]:
        """Extract tenant/brand data from the decoded message."""
        if not self.has_tenant_data():
            return {}

        # Look for list-type fields that might contain tenant data
        tenant_lists = {}
        for key, value in self.decoded_data.items():
            if isinstance(value, list) and value:
                # Check if list items look like tenant data
                if isinstance(value[0], dict) and any(
                    tenant_field in str(value[0]).lower()
                    for tenant_field in ["name", "category", "address", "rating"]
                ):
                    tenant_lists[key] = value

        return tenant_lists

    def get_field_summary(self) -> Dict[str, Any]:
        """Get a summary of the message fields."""
        if not self.decoded_data:
            return {"total_fields": 0, "field_types": {}}

        field_types = {}
        def count_types(data: Any, path: str = ""):
            if isinstance(data, dict):
                for key, value in data.items():
                    field_type = type(value).__name__
                    field_types[field_type] = field_types.get(field_type, 0) + 1
                    count_types(value, f"{path}.{key}")
            elif isinstance(data, list):
                field_types["list"] = field_types.get("list", 0) + 1
                for item in data[:3]:  # Sample first few items
                    count_types(item, f"{path}[]")

        count_types(self.decoded_data)

        return {
            "total_fields": len(field_types),
            "field_types": field_types,
            "has_tenant_data": self.has_tenant_data(),
        }

    def get_decode_info(self) -> Dict[str, Any]:
        """Get information about the decoding process."""
        return {
            "decode_time_seconds": self.decode_time,
            "confidence_score": self.confidence_score,
            "field_count": self.field_count,
            "schema_hash": self.schema_hash,
            "has_raw_bytes": self.raw_bytes is not None,
            "raw_bytes_size": len(self.raw_bytes) if self.raw_bytes else 0,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "schema_hash": self.schema_hash,
            "field_count": self.field_count,
            "decoded_data": self.decoded_data,
            "raw_bytes": self.raw_bytes.hex() if self.raw_bytes else None,
            "source_request_id": self.source_request_id,
            "confidence_score": self.confidence_score,
            "decode_time": self.decode_time,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProtobufMessage':
        """Create ProtobufMessage instance from dictionary."""
        # Handle raw_bytes conversion from hex string
        raw_bytes_hex = data.pop("raw_bytes", None)
        if raw_bytes_hex:
            data["raw_bytes"] = bytes.fromhex(raw_bytes_hex)

        return cls(**data)

    def is_valid(self) -> bool:
        """Check if protobuf message data is valid."""
        try:
            self._validate_fields()
            return True
        except ValueError:
            return False

    def get_data_summary(self) -> str:
        """Get a summary of the decoded data."""
        if not self.decoded_data:
            return "Empty message"

        summary = f"Fields: {self.field_count}, Confidence: {self.confidence_score:.2f}"
        if self.has_tenant_data():
            tenant_data = self.extract_tenant_data()
            total_tenants = sum(len(tenants) for tenants in tenant_data.values())
            summary += f", Tenants: {total_tenants}"

        return summary

    def __str__(self) -> str:
        """String representation of the protobuf message."""
        return f"ProtobufMessage(schema={self.schema_hash[:8]}..., fields={self.field_count}, confidence={self.confidence_score:.2f})"

    def __eq__(self, other) -> bool:
        """Equality based on schema hash and decoded data."""
        if not isinstance(other, ProtobufMessage):
            return False
        return (self.schema_hash == other.schema_hash and
                self.decoded_data == other.decoded_data)

    def __hash__(self) -> int:
        """Hash based on schema hash."""
        return hash(self.schema_hash)
