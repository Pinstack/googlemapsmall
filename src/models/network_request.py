"""NetworkRequest dataclass for HAR file entries.

Represents captured HAR file entries for forensic analysis.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Union
import json


@dataclass
class NetworkRequest:
    """Represents a network request captured in HAR format.

    Attributes:
        id: Unique request identifier
        url: Request URL
        method: HTTP method (GET, POST, etc.)
        headers: Request headers
        request_body: Request body if present
        response_status: HTTP status code
        response_headers: Response headers
        response_body: Response content
        response_size: Response size in bytes
        timing: Request timing information
        is_protobuf: Whether response is protobuf-encoded
        timestamp: When request was made
    """
    id: Optional[str] = None
    url: str = ""
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    request_body: Optional[Union[str, bytes]] = None
    response_status: int = 0
    response_headers: Dict[str, str] = field(default_factory=dict)
    response_body: Optional[Union[str, bytes]] = None
    response_size: int = field(init=False, default=0)
    timing: Optional[Dict[str, float]] = None
    is_protobuf: bool = field(init=False, default=False)
    timestamp: Optional[str] = None

    def __post_init__(self):
        """Validate and compute derived fields after initialization."""
        self._validate_required_fields()
        self._compute_derived_fields()

    def _validate_required_fields(self):
        """Validate required fields."""
        if not self.url or not isinstance(self.url, str):
            raise ValueError("URL must be a non-empty string")

        if not self.url.startswith("http"):
            raise ValueError(f"URL must start with http/https, got {self.url}")

        if not isinstance(self.method, str) or self.method not in ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]:
            raise ValueError(f"Invalid HTTP method: {self.method}")

        if not isinstance(self.response_status, int):
            raise ValueError("Response status must be an integer")

        if not 100 <= self.response_status <= 599:
            raise ValueError(f"Invalid HTTP status code: {self.response_status}")

    def _compute_derived_fields(self):
        """Compute response_size and is_protobuf from response data."""
        # Calculate response size
        if self.response_body:
            if isinstance(self.response_body, str):
                self.response_size = len(self.response_body.encode('utf-8'))
            elif isinstance(self.response_body, bytes):
                self.response_size = len(self.response_body)
            else:
                self.response_size = 0
        else:
            self.response_size = 0

        # Determine if response is protobuf
        content_type = self.response_headers.get("content-type", "").lower()
        self.is_protobuf = (
            "application/vnd.google.octet-stream-compressible" in content_type or
            "application/octet-stream" in content_type or
            self.url and "pb=" in self.url
        )

    def get_content_type(self) -> str:
        """Get the response content type."""
        return self.response_headers.get("content-type", "unknown")

    def is_successful(self) -> bool:
        """Check if the request was successful (2xx status)."""
        return 200 <= self.response_status <= 299

    def is_tenant_data_request(self) -> bool:
        """Check if this request likely contains tenant/brand data."""
        # Look for Google Maps specific patterns
        if "maps" not in self.url:
            return False

        # Check for known tenant data endpoints
        tenant_indicators = [
            "/preview/place",
            "/vt/stream",
            "pb=",  # Protobuf parameter
            "data=",  # Encoded data parameter
        ]

        url_lower = self.url.lower()
        return any(indicator in url_lower for indicator in tenant_indicators)

    def get_timing_summary(self) -> Dict[str, float]:
        """Get a summary of timing information."""
        if not self.timing:
            return {"total": 0.0}

        # Calculate total time from components
        total = sum(self.timing.values())
        return {
            "total": total,
            **self.timing
        }

    def extract_protobuf_params(self) -> Dict[str, str]:
        """Extract protobuf parameters from URL."""
        params = {}

        if "?" in self.url:
            query_string = self.url.split("?", 1)[1]
            for param in query_string.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    if key.startswith("pb") or "data" in key.lower():
                        params[key] = value

        return params

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "url": self.url,
            "method": self.method,
            "headers": self.headers,
            "request_body": self.request_body,
            "response_status": self.response_status,
            "response_headers": self.response_headers,
            "response_body": self.response_body,
            "response_size": self.response_size,
            "timing": self.timing,
            "is_protobuf": self.is_protobuf,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_har_entry(cls, har_entry: Dict[str, Any]) -> 'NetworkRequest':
        """Create NetworkRequest from HAR entry."""
        request = har_entry.get("request", {})
        response = har_entry.get("response", {})
        timing = har_entry.get("timings", {})

        return cls(
            url=request.get("url", ""),
            method=request.get("method", "GET"),
            headers={h["name"]: h["value"] for h in request.get("headers", [])},
            request_body=request.get("postData", {}).get("text") if request.get("postData") else None,
            response_status=response.get("status", 0),
            response_headers={h["name"]: h["value"] for h in response.get("headers", [])},
            response_body=response.get("content", {}).get("text"),
            timing=timing,
            timestamp=har_entry.get("startedDateTime"),
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkRequest':
        """Create NetworkRequest instance from dictionary."""
        return cls(**data)

    def is_valid(self) -> bool:
        """Check if network request data is valid."""
        try:
            self._validate_required_fields()
            return True
        except ValueError:
            return False

    def get_request_summary(self) -> str:
        """Get a summary of the request."""
        return f"{self.method} {self.url} → {self.response_status}"

    def __str__(self) -> str:
        """String representation of the network request."""
        return f"{self.method} {self.url} [{self.response_status}]"

    def __eq__(self, other) -> bool:
        """Equality based on URL and method."""
        if not isinstance(other, NetworkRequest):
            return False
        return self.url == other.url and self.method == other.method

    def __hash__(self) -> int:
        """Hash based on URL and method."""
        return hash((self.url, self.method))
