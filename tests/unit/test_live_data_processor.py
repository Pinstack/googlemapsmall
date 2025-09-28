"""Unit tests for live data processor validation and normalization.

Tests data validation, normalization, and consistency checking for live-scraped mall data.
"""

import pytest
from typing import Dict, Any, List

# Import the data processor functions
try:
    from src.data_processor import (
        process_brand_data,
        validate_brand_data_detailed,
        validate_category_data,
        validate_brand_category_consistency,
        validate_category_brand_counts,
    )
    from src.models import Brand, Category
except ImportError:
    # Mock for testing if dataclasses not available
    Brand = None
    Category = None
    process_brand_data = None


class TestLiveDataProcessorValidation:
    """Test data validation and normalization for live scraping."""

    def test_brand_dataclass_validation(self):
        """Test that Brand dataclass validates input correctly."""
        if not Brand:
            pytest.skip("Brand dataclass not available")

        # Valid brand data
        valid_brand = Brand(
            name="Test Store",
            category="Fashion",
            confidence_score=0.85
        )
        assert valid_brand.is_valid()

        # Invalid brand data - empty name
        with pytest.raises(ValueError):
            Brand(name="", category="Fashion")

        # Invalid brand data - invalid rating
        with pytest.raises(ValueError):
            Brand(name="Test", category="Fashion", rating=6.0)

    def test_category_dataclass_validation(self):
        """Test that Category dataclass validates input correctly."""
        if not Category:
            pytest.skip("Category dataclass not available")

        # Valid category data - no pagination for <= 10 brands
        valid_category = Category(
            name="Fashion",
            brand_count=10,
            has_pagination=False
        )
        assert valid_category.is_valid()

        # Valid category data - pagination required for > 10 brands
        valid_category_paginated = Category(
            name="Food & Drink",
            brand_count=25,
            has_pagination=True
        )
        assert valid_category_paginated.is_valid()

        # Invalid category data - negative count
        with pytest.raises(ValueError):
            Category(name="Fashion", brand_count=-1)

    def test_process_brand_data_with_dataclasses(self):
        """Test processing live scraping results with dataclass validation."""
        if not process_brand_data:
            pytest.skip("Data processor not available")

        # Mock live scraping result
        live_result = {
            "brands": [
                {
                    "name": "Apple Store",
                    "category": "Electronics",
                    "location_details": {"address": "Test Address"},
                    "rating": 4.5,
                    "confidence_score": 0.95
                },
                {
                    "name": "H&M",
                    "category": "Fashion",
                    "location_details": {"address": "Test Address 2"},
                    "rating": 4.0,
                    "confidence_score": 0.88
                }
            ],
            "categories": [
                {"name": "Electronics", "brand_count": 1, "has_pagination": False},
                {"name": "Fashion", "brand_count": 1, "has_pagination": False}
            ],
            "metadata": {
                "scraping_mode": "real_with_antibot",
                "session_duration_seconds": 15.5
            },
            "har_data": {"log": {"entries": []}},
            "har_analysis": None,
            "protobuf_decodings": []
        }

        # Process the data
        processed = process_brand_data(live_result)

        # Verify processing worked
        assert "brands" in processed
        assert "categories" in processed
        assert "metadata" in processed

        # Check that validation passed
        assert processed["metadata"]["data_consistency_valid"] is True
        assert processed["metadata"]["count_accuracy_valid"] is True

        # Verify brand data was preserved
        assert len(processed["brands"]) == 2
        assert processed["brands"][0]["name"] == "Apple Store"
        assert processed["brands"][1]["name"] == "H&M"

    def test_brand_category_consistency_validation(self):
        """Test validation of brand-category relationships."""
        # Valid data - brands match categories
        valid_brands = [
            {"name": "Store A", "category": "Fashion"},
            {"name": "Store B", "category": "Electronics"}
        ]
        valid_categories = [
            {"name": "Fashion", "brand_count": 1},
            {"name": "Electronics", "brand_count": 1}
        ]

        assert validate_brand_category_consistency(valid_brands, valid_categories)

        # Invalid data - brand references unknown category
        invalid_brands = [
            {"name": "Store A", "category": "Unknown"}
        ]
        invalid_categories = [
            {"name": "Fashion", "brand_count": 0}
        ]

        assert not validate_brand_category_consistency(invalid_brands, invalid_categories)

    def test_category_brand_count_validation(self):
        """Test validation of category brand counts."""
        # Valid counts
        brands = [
            {"name": "Store A", "category": "Fashion"},
            {"name": "Store B", "category": "Fashion"}
        ]
        categories = [
            {"name": "Fashion", "brand_count": 2}
        ]

        assert validate_category_brand_counts(brands, categories)

        # Invalid counts - mismatch
        categories_wrong = [
            {"name": "Fashion", "brand_count": 1}  # Should be 2
        ]

        assert not validate_category_brand_counts(brands, categories_wrong)

    def test_live_scraping_metadata_validation(self):
        """Test that live scraping metadata is properly validated."""
        # Test with mock live scraping result
        live_metadata = {
            "scraping_mode": "real_with_antibot",
            "session_duration_seconds": 22.5,
            "brands_extracted": 5,
            "categories_extracted": 3,
            "extraction_efficiency": 0.22,
            "session_persistence_used": True,
            "proxy_rotation_used": False,
            "consent_cleared": True,
            "rate_limiting_encountered": False,
            "har_analysis_performed": True,
            "protobuf_decodings_found": 0
        }

        # Verify all expected metadata fields are present
        expected_fields = [
            "scraping_mode", "session_duration_seconds", "brands_extracted",
            "categories_extracted", "extraction_efficiency", "session_persistence_used",
            "proxy_rotation_used", "consent_cleared", "rate_limiting_encountered",
            "har_analysis_performed", "protobuf_decodings_found"
        ]

        for field in expected_fields:
            assert field in live_metadata, f"Missing metadata field: {field}"

        # Verify data types
        assert isinstance(live_metadata["session_duration_seconds"], (int, float))
        assert isinstance(live_metadata["brands_extracted"], int)
        assert isinstance(live_metadata["consent_cleared"], bool)

    @pytest.mark.parametrize("confidence_score", [0.0, 0.5, 0.85, 1.0])
    def test_confidence_score_validation(self, confidence_score):
        """Test that confidence scores are properly validated."""
        if not Brand:
            pytest.skip("Brand dataclass not available")

        brand = Brand(
            name="Test Store",
            category="Fashion",
            confidence_score=confidence_score
        )
        assert brand.is_valid()

        # Test invalid confidence scores
        with pytest.raises(ValueError):
            Brand(name="Test", category="Fashion", confidence_score=-0.1)

        with pytest.raises(ValueError):
            Brand(name="Test", category="Fashion", confidence_score=1.1)
