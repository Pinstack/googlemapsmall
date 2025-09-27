# Contract: Browser Automation Module

**Contract ID**: BROWSER-AUTOMATION-001
**Version**: 1.0
**Date**: 2025-09-27

## Overview
The Browser Automation Module provides controlled web scraping capabilities for Google Maps mall directories. Uses Playwright for reliable browser control with HAR capture capabilities.

## Interface Definition

### Input
```python
def scrape_mall_directory(mall_url: str, strategy: dict) -> dict:
    """
    Scrape tenant directory from Google Maps mall page.

    Args:
        mall_url: Google Maps URL for the mall
        strategy: Dict specifying scraping approach (view_all, categories, etc.)

    Returns:
        Dict containing:
        - brands: List of extracted brand information
        - categories: List of discovered categories
        - har_data: Captured network traffic (optional)
        - metadata: Scraping session information
    """

def capture_har_during_interaction(mall_url: str, interaction_steps: list) -> dict:
    """
    Capture HAR file while performing specific interactions.

    Args:
        mall_url: Google Maps URL for the mall
        interaction_steps: List of interaction commands to execute

    Returns:
        Dict containing HAR data and interaction results
    """
```

### Output Schema
```json
{
  "brands": [
    {
      "name": "string",
      "category": "string",
      "location_details": "object",
      "confidence_score": "float"
    }
  ],
  "categories": [
    {
      "name": "string",
      "brand_count": "integer",
      "requires_pagination": "boolean"
    }
  ],
  "har_data": {
    "log": {
      "entries": "array"
    }
  },
  "metadata": {
    "session_duration": "float",
    "interactions_performed": "integer",
    "success_rate": "float",
    "errors_encountered": "array"
  }
}
```

## Contract Tests

### Test Case 1: Basic Mall Scraping
```python
def test_basic_mall_scraping():
    result = scrape_mall_directory(
        "https://www.google.com/maps/place/St+James+Quarter",
        {"strategy": "view_all"}
    )

    assert len(result["brands"]) > 0
    assert result["metadata"]["success_rate"] > 0.8
    assert "har_data" in result
```

### Test Case 2: Category-based Scraping
```python
def test_category_based_scraping():
    result = scrape_mall_directory(
        "https://www.google.com/maps/place/St+James+Quarter",
        {"strategy": "categories", "max_categories": 5}
    )

    assert len(result["categories"]) > 0
    assert all(cat["brand_count"] > 0 for cat in result["categories"])
    assert result["metadata"]["interactions_performed"] > 0
```

### Test Case 3: HAR Capture Integration
```python
def test_har_capture_integration():
    result = capture_har_during_interaction(
        "https://www.google.com/maps/place/St+James+Quarter",
        ["navigate", "wait_for_tenant_directory", "click_view_all"]
    )

    assert result["har_data"]["log"]["entries"]
    entries = result["har_data"]["log"]["entries"]
    assert any("maps" in entry["request"]["url"] for entry in entries)
```

## Error Handling
- **NavigationError**: When page fails to load
- **ElementNotFound**: When expected DOM elements are missing
- **TimeoutError**: When operations exceed time limits
- **AntiBotDetected**: When bot detection measures are triggered
- **HARCaptureError**: When network capture fails

## Performance Requirements
- Page load timeout: <30 seconds
- Scraping completion: <2 minutes for ~150 brands
- Memory usage: <200MB during operation
- HAR file size: <50MB for typical session

## Anti-Bot Evasion Strategies
- Randomized delays between interactions (500ms-2000ms)
- Human-like mouse movement patterns
- Realistic viewport scrolling
- Session cookie management
- User agent rotation (within browser family)

## Interaction Patterns

### View All Strategy
1. Navigate to mall URL
2. Wait for tenant directory to load
3. Click "View All" or equivalent button
4. Extract all visible brands
5. Return results

### Category Strategy
1. Navigate to mall URL
2. Identify available categories
3. For each category:
   - Click category
   - Handle pagination if >10 brands
   - Extract brands
4. Deduplicate across categories
5. Return consolidated results

### HAR Capture Strategy
1. Start HAR recording
2. Perform specified interactions
3. Stop recording and return HAR data
4. Optionally extract brands from DOM
