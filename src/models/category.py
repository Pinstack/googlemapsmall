"""Category dataclass for Google Maps mall scraping.

Represents groupings of similar brands within the mall directory.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Category:
    """Represents a category grouping brands within a mall.

    Attributes:
        id: Unique identifier
        name: Category name (e.g., "Fashion", "Electronics")
        brand_count: Number of brands in this category
        has_pagination: Whether category requires scrolling (>10 brands)
    """
    id: Optional[str] = None
    name: str = ""
    brand_count: int = 0
    has_pagination: bool = False

    def __post_init__(self):
        """Validate dataclass after initialization."""
        self._validate_fields()

    def _validate_fields(self):
        """Validate all fields according to business rules."""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Category name must be a non-empty string")

        # Validate name is unique within mall (checked at aggregation level)
        if not self.name.strip():
            raise ValueError("Category name cannot be only whitespace")

        if not isinstance(self.brand_count, int) or self.brand_count < 0:
            raise ValueError(f"Brand count must be a non-negative integer, got {self.brand_count}")

        if not isinstance(self.has_pagination, bool):
            raise ValueError("Has pagination must be a boolean")

        # Business rule: categories with >10 brands should have pagination
        expected_pagination = self.brand_count > 10
        if self.has_pagination != expected_pagination:
            raise ValueError(
                f"Pagination flag inconsistency: category with {self.brand_count} brands "
                f"should have pagination={expected_pagination}, got {self.has_pagination}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "brand_count": self.brand_count,
            "has_pagination": self.has_pagination,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Category':
        """Create Category instance from dictionary."""
        return cls(**data)

    def is_valid(self) -> bool:
        """Check if category data meets validation requirements."""
        try:
            self._validate_fields()
            return True
        except ValueError:
            return False

    def requires_pagination(self) -> bool:
        """Check if this category requires pagination based on brand count."""
        return self.brand_count > 10

    def get_pagination_info(self) -> Dict[str, Any]:
        """Get pagination information for this category."""
        return {
            "category_name": self.name,
            "total_brands": self.brand_count,
            "requires_pagination": self.has_pagination,
            "estimated_pages": max(1, (self.brand_count + 9) // 10) if self.has_pagination else 1,
        }

    def update_brand_count(self, new_count: int):
        """Update brand count and recalculate pagination flag."""
        self.brand_count = new_count
        self.has_pagination = self.requires_pagination()
        self._validate_fields()  # Re-validate after update

    def __str__(self) -> str:
        """String representation of the category."""
        pagination_indicator = " (paginated)" if self.has_pagination else ""
        return f"{self.name}: {self.brand_count} brands{pagination_indicator}"

    def __eq__(self, other) -> bool:
        """Equality based on name."""
        if not isinstance(other, Category):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        """Hash based on name."""
        return hash(self.name)

    def __lt__(self, other) -> bool:
        """Sort categories by brand count (descending)."""
        if not isinstance(other, Category):
            return NotImplemented
        return self.brand_count > other.brand_count  # Descending order
