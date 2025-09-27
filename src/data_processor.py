"""Data Processor Module for Google Maps Mall Scraping.

Handles data validation, processing, and consistency checking for extracted mall data.
Validates Brand, Category, Mall entities and ensures data integrity.
"""  # noqa: E501

import re
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse


def validate_brand_data(brand: Dict[str, Any]) -> bool:
    """Validate brand entity data according to business rules.

    Args:
        brand: Brand data dictionary

    Returns:
        True if valid, False otherwise
    """
    # Required fields validation
    if not _validate_brand_name(brand.get("name")):
        return False

    if not _validate_brand_category(brand.get("category")):
        return False

    # Optional fields validation
    if "rating" in brand and brand["rating"] is not None:
        if not _validate_brand_rating(brand["rating"]):
            return False

    if "phone" in brand and brand.get("phone"):
        if not _validate_brand_phone(brand["phone"]):
            return False

    if "website" in brand and brand.get("website"):
        if not _validate_brand_url(brand["website"]):
            return False

    return True


def validate_category_data(category: Dict[str, Any]) -> bool:
    """Validate category entity data according to business rules.

    Args:
        category: Category data dictionary

    Returns:
        True if valid, False otherwise
    """
    # Required fields validation
    if not _validate_category_name(category.get("name")):
        return False

    if not _validate_category_brand_count(category.get("brand_count")):
        return False

    # Optional pagination flag validation
    if "has_pagination" in category:
        brand_count = category.get("brand_count", 0)
        has_pagination = category.get("has_pagination", False)
        if not _validate_pagination_flag(brand_count, has_pagination):
            return False

    return True


def validate_mall_data(mall: Dict[str, Any]) -> bool:
    """Validate mall entity data according to business rules.

    Args:
        mall: Mall data dictionary

    Returns:
        True if valid, False otherwise
    """
    # Required fields validation
    if not _validate_mall_name(mall.get("name")):
        return False

    if not _validate_mall_coordinates(mall.get("latitude"), mall.get("longitude")):
        return False

    if not _validate_mall_id(mall.get("id")):
        return False

    return True


def validate_network_data_integrity(network_data: Dict[str, Any]) -> bool:
    """Validate network data integrity.

    Args:
        network_data: Network data dictionary

    Returns:
        True if valid, False otherwise
    """
    # Check if protobuf decoded successfully
    if not network_data.get("protobuf_decoded", True):
        return False

    # Check response size is reasonable
    response_size = network_data.get("response_size", 0)
    if response_size <= 0 or response_size > 50 * 1024 * 1024:  # 50MB max
        return False

    # Check decode time is reasonable
    decode_time = network_data.get("decode_time", 0)
    if decode_time < 0 or decode_time > 10.0:  # Max 10 seconds
        return False

    return True


def validate_request_response_correlation(
    request_response_pair: Dict[str, Any],
) -> bool:
    """Validate request/response correlation.

    Args:
        request_response_pair: Dict with request and response data

    Returns:
        True if properly correlated, False otherwise  # noqa: E501
    """
    if (
        "request" not in request_response_pair
        or "response" not in request_response_pair
    ):
        return False

    request = request_response_pair["request"]
    response = request_response_pair["response"]

    # Check required fields exist
    if not request.get("url") or not request.get("method"):
        return False

    if "status" not in response:
        return False

    # Check URL correlation (response should relate to request)
    request_url = request["url"]
    if not isinstance(request_url, str) or not request_url.startswith("http"):
        return False

    return True


def validate_timing_data(timing_data: Dict[str, Any]) -> bool:
    """Validate network timing data.

    Args:
        timing_data: Timing data dictionary

    Returns:
        True if timing data is valid, False otherwise
    """
    required_fields = ["blocked", "dns", "connect", "send", "wait", "receive", "ssl"]

    # Check all required fields exist and are non-negative
    for field in required_fields:
        if field not in timing_data:
            return False

        value = timing_data[field]
        if not isinstance(value, (int, float)) or value < 0:
            return False

        # Check for unreasonably long timing (more than 5 minutes)
        if value >= 300.0:
            return False

    # Check total timing is reasonable
    total_time = sum(timing_data.values())
    if total_time > 600.0:  # More than 10 minutes total
        return False

    return True


def validate_brand_category_consistency(
    brands: List[Dict[str, Any]], categories: List[Dict[str, Any]]
) -> bool:
    """Validate consistency between brands and categories.

    Args:
        brands: List of brand dictionaries
        categories: List of category dictionaries

    Returns:
        True if consistent, False otherwise
    """
    # Create category name to category mapping
    category_names = {cat["name"] for cat in categories if cat.get("name")}

    # Check all brands reference valid categories
    for brand in brands:
        brand_category = brand.get("category")
        if brand_category and brand_category not in category_names:
            return False

    return True


def validate_category_brand_counts(
    brands: List[Dict[str, Any]], categories: List[Dict[str, Any]]
) -> bool:
    """Validate that category brand counts match actual brand counts.

    Args:
        brands: List of brand dictionaries
        categories: List of category dictionaries

    Returns:
        True if counts are accurate, False otherwise  # noqa: E501
    """
    # Count brands per category
    actual_counts: Dict[str, int] = {}
    for brand in brands:
        category = brand.get("category")
        if category:
            actual_counts[category] = actual_counts.get(category, 0) + 1

    # Check declared counts match actual counts
    for category in categories:
        category_name = category.get("name")
        declared_count = category.get("brand_count", 0)

        actual_count = actual_counts.get(category_name, 0)

        if declared_count != actual_count:
            return False

    return True


# Helper validation functions


def _validate_brand_name(name: Optional[str]) -> bool:
    """Validate brand name (2-100 characters, non-empty)."""
    if not name or not isinstance(name, str):
        return False

    name_len = len(name.strip())
    return 2 <= name_len <= 100


def _validate_brand_category(category: Optional[str]) -> bool:
    """Validate brand category (non-empty string)."""
    return bool(category and isinstance(category, str) and category.strip())


def _validate_brand_rating(rating: Union[int, float, None]) -> bool:
    """Validate brand rating (0.0-5.0 if present)."""
    if rating is None:
        return True

    # Must be numeric type, not string
    if not isinstance(rating, (int, float)):
        return False

    return 0.0 <= rating <= 5.0


def _validate_brand_phone(phone: str) -> bool:
    """Validate brand phone number (basic international format check)."""
    if not phone or not isinstance(phone, str):
        return False

    # Basic phone validation - should contain digits and reasonable length
    digits_only = re.sub(r"[^\d]", "", phone)
    return len(digits_only) >= 7 and len(phone) <= 20


def _validate_brand_url(url: str) -> bool:
    """Validate brand URL."""
    if not url or not isinstance(url, str):
        return False

    try:
        parsed = urlparse(url)
        return bool(parsed.scheme in ["http", "https"] and parsed.netloc)
    except Exception:
        return False


def _validate_category_name(name: Optional[str]) -> bool:
    """Validate category name (non-empty, unique within mall)."""
    return bool(name and isinstance(name, str) and name.strip())


def _validate_category_brand_count(count: Union[int, None]) -> bool:
    """Validate category brand count (>= 0)."""
    try:
        return count is not None and isinstance(count, int) and count >= 0
    except (TypeError, ValueError):
        return False


def _validate_pagination_flag(brand_count: int, has_pagination: bool) -> bool:
    """Validate pagination flag based on brand count."""
    # Categories with > 10 brands should have pagination
    # Categories with <= 10 brands should not have pagination
    expected_pagination = brand_count > 10
    return has_pagination == expected_pagination


def _validate_mall_name(name: Optional[str]) -> bool:
    """Validate mall name (non-empty)."""
    return bool(name and isinstance(name, str) and name.strip())


def _validate_mall_coordinates(
    latitude: Union[float, int, None], longitude: Union[float, int, None]
) -> bool:
    """Validate mall coordinates."""
    # Must be numeric types, not strings
    if not isinstance(latitude, (int, float)) or not isinstance(
        longitude, (int, float)
    ):
        return False

    # Check latitude range (-90 to 90)
    if not -90.0 <= latitude <= 90.0:
        return False

    # Check longitude range (-180 to 180)
    if not -180.0 <= longitude <= 180.0:
        return False

    return True


def _validate_mall_id(place_id: Optional[str]) -> bool:
    """Validate Google Maps place ID format."""
    if not place_id or not isinstance(place_id, str):
        return False

    # Google Places IDs typically start with "ChIJ" and are 20+ characters
    return place_id.startswith("ChIJ") and len(place_id) >= 10


def process_brand_data(scraping_result: Dict[str, Any]) -> Dict[str, Any]:
    """Process and validate raw scraping results into clean, structured data.

    Args:
        scraping_result: Raw scraping result from scraper module

    Returns:
        Processed result with validated data and processing metadata
    """
    # Extract raw data
    raw_brands = scraping_result.get("brands", [])
    raw_categories = scraping_result.get("categories", [])
    metadata = scraping_result.get("metadata", {})
    har_data = scraping_result.get("har_data", {})

    # Validate and clean brand data
    validated_brands = []
    brand_errors = []

    for i, brand in enumerate(raw_brands):
        validation_result = validate_brand_data_detailed(brand)
        if validation_result["is_valid"]:
            validated_brands.append(brand)
        else:
            brand_errors.extend(validation_result["errors"])

    # Validate and clean category data
    validated_categories = []
    category_errors = []

    for i, category in enumerate(raw_categories):
        if validate_category_data(category):
            validated_categories.append(category)
        else:
            category_errors.append(f"Category {i}: validation failed")

    # Validate brand-category consistency
    consistency_valid = validate_brand_category_consistency(
        validated_brands, validated_categories
    )
    count_valid = validate_category_brand_counts(validated_brands, validated_categories)

    # Calculate processing metrics
    processing_metadata = {
        "brands_processed": len(validated_brands),
        "brands_rejected": len(brand_errors),
        "categories_processed": len(validated_categories),
        "categories_rejected": len(category_errors),
        "total_brands_input": len(raw_brands),
        "total_categories_input": len(raw_categories),
        "data_consistency_valid": consistency_valid,
        "count_accuracy_valid": count_valid,
        "processing_errors": brand_errors + category_errors,
        "processing_success_rate": (len(validated_brands) + len(validated_categories))
        / max(1, len(raw_brands) + len(raw_categories)),
    }

    # Combine original metadata with processing metadata
    combined_metadata = {**metadata, **processing_metadata}

    return {
        "brands": validated_brands,
        "categories": validated_categories,
        "har_data": har_data,
        "metadata": combined_metadata,
    }


def validate_brand_data_detailed(brand: Dict[str, Any]) -> Dict[str, Any]:
    """Validate brand data and return validation result with errors.

    Args:
        brand: Brand data to validate

    Returns:
        Dict with is_valid, errors, and warnings
    """
    errors = []
    warnings = []

    # Required field validation
    if not _validate_brand_name(brand.get("name")):
        errors.append("Invalid or missing name")

    if not _validate_brand_category(brand.get("category")):
        errors.append("Invalid or missing category")

    # Optional field validation
    if "rating" in brand and brand["rating"] is not None:
        if not _validate_brand_rating(brand["rating"]):
            errors.append("Invalid rating (must be 0.0-5.0)")

    if "phone" in brand and brand.get("phone"):
        if not _validate_brand_phone(brand["phone"]):
            errors.append("Invalid phone number format")

    if "website" in brand and brand.get("website"):
        if not _validate_brand_url(brand["website"]):
            errors.append("Invalid website URL")

    # Additional validations
    if "review_count" in brand and brand.get("review_count") is not None:
        if not isinstance(brand["review_count"], int) or brand["review_count"] < 0:
            warnings.append("Invalid review count")

    return {"is_valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def deduplicate_brands(scraping_result: Dict[str, Any]) -> Dict[str, Any]:
    """Remove duplicate brands from scraping results.

    Args:
        scraping_result: Raw scraping result with potential duplicates

    Returns:
        Deduplicated result with unique brands
    """
    raw_brands = scraping_result.get("brands", [])
    categories = scraping_result.get("categories", [])
    metadata = scraping_result.get("metadata", {})
    har_data = scraping_result.get("har_data", {})

    # Deduplicate brands by name (case-insensitive)
    seen_names = set()
    deduplicated_brands = []

    for brand in raw_brands:
        name = brand.get("name", "").strip().lower()
        if name and name not in seen_names:
            seen_names.add(name)
            deduplicated_brands.append(brand)

    # Update category counts to reflect deduplication
    updated_categories = []
    for category in categories:
        category_name = category.get("name")
        if category_name:
            # Recount brands in this category
            category_brand_count = sum(
                1
                for brand in deduplicated_brands
                if brand.get("category") == category_name
            )
            updated_category = {**category, "brand_count": category_brand_count}
            updated_categories.append(updated_category)

    # Update metadata
    deduplication_metadata = {
        "original_brand_count": len(raw_brands),
        "deduplicated_brand_count": len(deduplicated_brands),
        "duplicates_removed": len(raw_brands) - len(deduplicated_brands),
        "deduplication_applied": True,
    }

    combined_metadata = {**metadata, **deduplication_metadata}

    return {
        "brands": deduplicated_brands,
        "categories": updated_categories,
        "har_data": har_data,
        "metadata": combined_metadata,
    }
