"""Brand dataclass for Google Maps mall scraping.

Represents individual stores/tenants within a shopping mall.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from urllib.parse import urlparse


@dataclass
class Brand:
    """Represents a brand/store within a mall.

    Attributes:
        id: Unique identifier (extracted from Google Maps)
        name: Brand/store name
        category: Business category (e.g., "Fashion", "Food & Drink")
        floor_level: Floor location if available
        operating_hours: Hours of operation
        phone: Contact phone number
        website: Brand website URL
        rating: Google Maps rating (0.0-5.0)
        review_count: Number of reviews
        confidence_score: Extraction confidence (0.0-1.0)
    """
    id: Optional[str] = None
    name: str = ""
    category: str = ""
    floor_level: Optional[str] = None
    operating_hours: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    confidence_score: float = 0.0

    def __post_init__(self):
        """Validate dataclass after initialization."""
        self._validate_required_fields()
        self._validate_optional_fields()

    def _validate_required_fields(self):
        """Validate required fields according to business rules."""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Brand name must be a non-empty string")

        if not self.category or not isinstance(self.category, str):
            raise ValueError("Brand category must be a non-empty string")

        # Validate name length (2-100 characters)
        name_len = len(self.name.strip())
        if not 2 <= name_len <= 100:
            raise ValueError(f"Brand name must be 2-100 characters, got {name_len}")

    def _validate_optional_fields(self):
        """Validate optional fields if present."""
        if self.rating is not None:
            if not isinstance(self.rating, (int, float)):
                raise ValueError("Rating must be numeric")
            if not 0.0 <= self.rating <= 5.0:
                raise ValueError(f"Rating must be 0.0-5.0, got {self.rating}")

        if self.review_count is not None:
            if not isinstance(self.review_count, int) or self.review_count < 0:
                raise ValueError("Review count must be a non-negative integer")

        if self.website and self.website.strip():
            self._validate_website(self.website)

        if self.phone and self.phone.strip():
            self._validate_phone(self.phone)

        if self.confidence_score < 0.0 or self.confidence_score > 1.0:
            raise ValueError(f"Confidence score must be 0.0-1.0, got {self.confidence_score}")

    def _validate_website(self, website: str):
        """Validate website URL format."""
        try:
            parsed = urlparse(website)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid website URL: {website}")
        except Exception:
            raise ValueError(f"Invalid website URL: {website}")

    def _validate_phone(self, phone: str):
        """Validate phone number format (basic validation)."""
        # Remove all non-digit characters
        digits_only = ''.join(c for c in phone if c.isdigit())
        if len(digits_only) < 7 or len(phone) > 20:
            raise ValueError(f"Invalid phone number format: {phone}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "floor_level": self.floor_level,
            "operating_hours": self.operating_hours,
            "phone": self.phone,
            "website": self.website,
            "rating": self.rating,
            "review_count": self.review_count,
            "confidence_score": self.confidence_score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Brand':
        """Create Brand instance from dictionary."""
        return cls(**data)

    def is_valid(self) -> bool:
        """Check if brand data meets validation requirements."""
        try:
            self._validate_required_fields()
            self._validate_optional_fields()
            return True
        except ValueError:
            return False

    def get_location_summary(self) -> str:
        """Get a summary of the brand's location."""
        if self.floor_level:
            return f"{self.floor_level}"
        return "Location not specified"

    def __str__(self) -> str:
        """String representation of the brand."""
        rating_str = f" ({self.rating}⭐)" if self.rating else ""
        return f"{self.name} - {self.category}{rating_str}"

    def __eq__(self, other) -> bool:
        """Equality based on name and category."""
        if not isinstance(other, Brand):
            return False
        return self.name == other.name and self.category == other.category

    def __hash__(self) -> int:
        """Hash based on name and category."""
        return hash((self.name, self.category))
