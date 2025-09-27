# Data Model: Google Maps Mall Scraping POC

**Version**: 1.0
**Date**: 2025-09-27
**Scope**: Single mall tenant extraction POC

## Overview

The data model represents the entities and relationships involved in extracting tenant/brand information from Google Maps mall directories. The model is designed for efficient scraping operations with network analysis insights.

## Core Entities

### Brand Entity
Represents individual stores/tenants within a shopping mall.

**Attributes**:
- `id`: Unique identifier (string, extracted from Google Maps)
- `name`: Brand/store name (string, required)
- `category`: Business category (string, e.g., "Fashion", "Food & Drink")
- `floor_level`: Floor location if available (string, optional)
- `operating_hours`: Hours of operation (string, optional)
- `phone`: Contact phone number (string, optional)
- `website`: Brand website URL (string, optional)
- `rating`: Google Maps rating (float, 0.0-5.0, optional)
- `review_count`: Number of reviews (integer, optional)

**Validation Rules**:
- `name` must be non-empty string
- `category` must be non-empty string
- `id` must be unique within mall
- All optional fields can be null/empty

**Relationships**:
- Belongs to one Category
- Belongs to one Mall

### Category Entity
Represents groupings of similar brands within the mall directory.

**Attributes**:
- `id`: Unique identifier (string, auto-generated)
- `name`: Category name (string, required, e.g., "Fashion", "Electronics")
- `brand_count`: Number of brands in category (integer, computed)
- `has_pagination`: Whether category has >10 brands requiring scrolling (boolean)

**Validation Rules**:
- `name` must be non-empty and unique within mall
- `brand_count` must be >= 0

**Relationships**:
- Has many Brands
- Belongs to one Mall

### Mall Entity
Represents the physical shopping center being scraped.

**Attributes**:
- `id`: Google Maps place ID (string, required)
- `name`: Mall name (string, required, e.g., "St James Quarter")
- `latitude`: Geographic latitude (float, required)
- `longitude`: Geographic longitude (float, required)
- `address`: Full address (string, optional)
- `total_brands`: Total number of brands extracted (integer, computed)
- `categories_count`: Number of categories found (integer, computed)

**Validation Rules**:
- `id` must match Google Maps place ID format
- `name` must be non-empty
- Coordinates must be valid geographic coordinates

**Relationships**:
- Has many Categories
- Has many Brands (through Categories)

### NetworkRequest Entity
Represents captured HAR file entries for forensic analysis.

**Attributes**:
- `id`: Unique request identifier (string, auto-generated)
- `url`: Request URL (string, required)
- `method`: HTTP method (string, required, e.g., "GET", "POST")
- `headers`: Request headers (JSON object, required)
- `request_body`: Request body if present (string/binary, optional)
- `response_status`: HTTP status code (integer, required)
- `response_headers`: Response headers (JSON object, required)
- `response_body`: Response content (string/binary, optional)
- `response_size`: Response size in bytes (integer, computed)
- `timing`: Request timing information (JSON object, optional)
- `is_protobuf`: Whether response is protobuf-encoded (boolean, computed)

**Validation Rules**:
- `url` must be valid URL format
- `method` must be valid HTTP method
- Response status should be in 200-599 range

**Relationships**:
- Associated with Mall (context of capture)
- May contain Brand data in response_body

### ProtobufMessage Entity
Represents decoded protobuf structures from network responses.

**Attributes**:
- `id`: Unique message identifier (string, auto-generated)
- `schema_hash`: Hash of inferred schema (string, computed)
- `field_count`: Number of top-level fields (integer, computed)
- `decoded_data`: Fully decoded protobuf structure (JSON object, required)
- `raw_bytes`: Original protobuf bytes (binary, optional for debugging)
- `source_request_id`: Reference to originating NetworkRequest (string, required)

**Validation Rules**:
- `decoded_data` must be valid JSON
- `schema_hash` should be consistent for similar message types

**Relationships**:
- Belongs to NetworkRequest
- May contain Brand/Category data in decoded_data

## Data Flow Relationships

### Scraping Pipeline
```
Mall → Categories → Brands
   ↓        ↓        ↓
NetworkRequest → ProtobufMessage → Extracted Data
```

### Forensic Analysis Flow
```
HAR File → NetworkRequest → ProtobufMessage → Schema Inference → Parameter Reconstruction
```

## Data Validation Rules

### Brand Data Quality
- Name should be 2-100 characters
- Category should match known mall categories
- Phone numbers should follow international format if present
- URLs should be valid if present
- Ratings should be 0.0-5.0 if present

### Category Consistency
- Categories should be consistent across scraping sessions
- Brand counts should match actual extracted brands
- Pagination flags should reflect actual data volume

### Network Data Integrity
- All protobuf responses should decode successfully
- Request/response pairs should be properly correlated
- Timing data should be within reasonable bounds

## Performance Considerations

### Memory Usage
- ProtobufMessage objects may contain large decoded_data structures
- NetworkRequest objects include full response bodies for analysis
- Consider streaming processing for large HAR files

### Storage Strategy
- JSON export for final brand data (human-readable, API-ready)
- HAR files retained for forensic reference
- Protobuf schemas cached for performance

### Scalability Limits
- Designed for single mall POC (~150 brands)
- Memory usage scales with response sizes
- Processing time scales with HAR file complexity

## Future Extensions

### Multi-Mall Support
- Mall entity becomes parent in hierarchy
- Cross-mall brand deduplication needed
- Geographic clustering capabilities

### Real-time Updates
- Timestamp tracking for data freshness
- Change detection mechanisms
- Incremental update strategies

### Advanced Analytics
- Brand category analysis
- Geographic distribution patterns
- Temporal change tracking
