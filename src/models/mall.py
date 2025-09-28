"""Mall dataclass for Google Maps mall scraping.

Represents the physical shopping center being scraped.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from .brand import Brand
from .category import Category


@dataclass
class Mall:
    """Represents a shopping mall with its brands and categories.

    Attributes:
        id: Google Maps place ID
        name: Mall name (e.g., "St James Quarter")
        latitude: Geographic latitude
        longitude: Geographic longitude
        address: Full address
        total_brands: Total number of brands (computed)
        categories_count: Number of categories (computed)
        brands: List of all brands in the mall
        categories: List of all categories in the mall
    """
    id: str = ""
    name: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    address: Optional[str] = None
    total_brands: int = field(init=False, default=0)
    categories_count: int = field(init=False, default=0)
    brands: List[Brand] = field(default_factory=list)
    categories: List[Category] = field(default_factory=list)

    def __post_init__(self):
        """Validate and compute derived fields after initialization."""
        self._validate_required_fields()
        self._validate_coordinates()
        self._validate_place_id()
        self._compute_derived_fields()

    def _validate_required_fields(self):
        """Validate required fields."""
        if not self.id or not isinstance(self.id, str):
            raise ValueError("Mall ID (place ID) must be a non-empty string")

        if not self.name or not isinstance(self.name, str):
            raise ValueError("Mall name must be a non-empty string")

        if not self.name.strip():
            raise ValueError("Mall name cannot be only whitespace")

    def _validate_coordinates(self):
        """Validate geographic coordinates."""
        if not isinstance(self.latitude, (int, float)):
            raise ValueError("Latitude must be numeric")

        if not isinstance(self.longitude, (int, float)):
            raise ValueError("Longitude must be numeric")

        # Check coordinate ranges
        if not -90.0 <= self.latitude <= 90.0:
            raise ValueError(f"Latitude must be -90 to 90, got {self.latitude}")

        if not -180.0 <= self.longitude <= 180.0:
            raise ValueError(f"Longitude must be -180 to 180, got {self.longitude}")

    def _validate_place_id(self):
        """Validate Google Maps place ID format."""
        if not self.id.startswith("ChIJ"):
            raise ValueError(f"Place ID must start with 'ChIJ', got {self.id}")

        if len(self.id) < 10:
            raise ValueError(f"Place ID too short, got {len(self.id)} characters")

    def _compute_derived_fields(self):
        """Compute total_brands and categories_count from lists."""
        self.total_brands = len(self.brands)
        self.categories_count = len(self.categories)

    def add_brand(self, brand: Brand):
        """Add a brand to the mall."""
        if not isinstance(brand, Brand):
            raise ValueError("Must be a Brand instance")

        self.brands.append(brand)
        self._compute_derived_fields()

    def add_category(self, category: Category):
        """Add a category to the mall."""
        if not isinstance(category, Category):
            raise ValueError("Must be a Category instance")

        # Check for duplicate category names
        if any(cat.name == category.name for cat in self.categories):
            raise ValueError(f"Category '{category.name}' already exists in mall")

        self.categories.append(category)
        self._compute_derived_fields()

    def remove_brand(self, brand: Brand):
        """Remove a brand from the mall."""
        self.brands = [b for b in self.brands if b != brand]
        self._compute_derived_fields()

    def remove_category(self, category: Category):
        """Remove a category from the mall."""
        self.categories = [c for c in self.categories if c != category]
        self._compute_derived_fields()

    def get_brands_by_category(self, category_name: str) -> List[Brand]:
        """Get all brands in a specific category."""
        return [brand for brand in self.brands if brand.category == category_name]

    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Get category by name."""
        for category in self.categories:
            if category.name == name:
                return category
        return None

    def validate_consistency(self) -> Dict[str, Any]:
        """Validate that mall data is internally consistent."""
        issues = []

        # Check brand-category consistency
        category_names = {cat.name for cat in self.categories}
        for brand in self.brands:
            if brand.category not in category_names:
                issues.append(f"Brand '{brand.name}' references unknown category '{brand.category}'")

        # Check category brand counts
        for category in self.categories:
            actual_count = len(self.get_brands_by_category(category.name))
            if category.brand_count != actual_count:
                issues.append(
                    f"Category '{category.name}' has count {category.brand_count} "
                    f"but found {actual_count} brands"
                )

        return {
            "is_consistent": len(issues) == 0,
            "issues": issues,
            "total_brands": self.total_brands,
            "total_categories": self.categories_count,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "total_brands": self.total_brands,
            "categories_count": self.categories_count,
            "brands": [brand.to_dict() for brand in self.brands],
            "categories": [category.to_dict() for category in self.categories],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Mall':
        """Create Mall instance from dictionary."""
        brands_data = data.pop("brands", [])
        categories_data = data.pop("categories", [])

        # Create mall without brands/categories first
        mall = cls(**data)

        # Add brands and categories
        for brand_data in brands_data:
            mall.add_brand(Brand.from_dict(brand_data))

        for category_data in categories_data:
            mall.add_category(Category.from_dict(category_data))

        return mall

    def is_valid(self) -> bool:
        """Check if mall data meets all validation requirements."""
        try:
            self._validate_required_fields()
            self._validate_coordinates()
            self._validate_place_id()

            # Validate all brands and categories
            for brand in self.brands:
                if not brand.is_valid():
                    return False

            for category in self.categories:
                if not category.is_valid():
                    return False

            # Validate consistency
            consistency = self.validate_consistency()
            return consistency["is_consistent"]

        except ValueError:
            return False

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the mall."""
        return {
            "name": self.name,
            "location": f"{self.latitude:.6f}, {self.longitude:.6f}",
            "total_brands": self.total_brands,
            "categories": self.categories_count,
            "top_categories": sorted(self.categories, reverse=True)[:3],  # By brand count
        }

    def __str__(self) -> str:
        """String representation of the mall."""
        return f"{self.name} ({self.total_brands} brands, {self.categories_count} categories)"

    def __eq__(self, other) -> bool:
        """Equality based on place ID."""
        if not isinstance(other, Mall):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on place ID."""
        return hash(self.id)
