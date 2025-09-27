# Google Maps Forensic Analysis Report

**Analysis Date**: 2025-09-27
**Target**: St James Quarter Mall, Edinburgh
**Google Maps URL**: https://www.google.com/maps/place/St+James+Quarter/@55.9549949,-3.1895632,18z/data=!3m1!5s0x4887c78e8d34be11:0x8f6f33443851f595!4m11!1m2!2m1!1sshopping+mall!3m7!1s0x4887c78e6281b45d:0xc4ad4b61a12fde3f!8m2!3d55.9552777!4d-3.1885505!10e3!15sCg1zaG9wcGluZyBtYWxsWg8iDXNob3BwaW5nIG1hbGySAQ9zaG9wcGluZ19jZW50ZXKaAURDaTlEUVVsUlFVTnZaRU5vZEhsalJqbHZUMnR3TkZac1ZuSlJNR2gwVkZoR1FtTlVWalZSTVVKUFVUQXdNMWRWUlJBQqoBSBABKhEiDXNob3BwaW5nIG1hbGwoADIeEAEiGkuN7owLLzlQ1GoPfJ4fLH5CMYQ0pkjwUtp7MhEQAiINc2hvcHBpbmcgbWFsbOABAPoBBAgAEEA!16s%2Fg%2F1hdz1tl0h?entry=ttu&g_ep=EgoyMDI1MDkyNC4wIKXMDSoASAFQAw%3D%3D

## Executive Summary

Google Maps uses a sophisticated multi-layered architecture for mall tenant data. The system combines:

1. **Initial Place Loading**: `/maps/preview/place` endpoint with protobuf parameters
2. **Vector Tile Streaming**: `/maps/vt/stream` for map data and indoor information
3. **Dynamic Content Loading**: JavaScript-driven data fetching for tenant directories
4. **Complex Parameter Encoding**: Base64/protobuf encoded request parameters

## Key Findings

### 1. Primary Data Endpoints

#### `/maps/preview/place` Endpoint
- **Purpose**: Initial place data loading
- **Parameters**: Complex protobuf-encoded `pb=!` parameter
- **Response**: JSON format (392,242 bytes observed)
- **Authentication**: Uses `authuser=0` parameter
- **Content-Type**: `application/json; charset=UTF-8`

**Sample Parameter Structure**:
```
pb=!1m16!1s[PLACE_ID]!3m8!1m3!1d725.6537156345426!2d[LONGITUDE]!3d[LATITUDE]!3m2!1i1492!2i499!4f13.1!4m2!3d[LATITUDE]!4d[LONGITUDE]!15m2!1m1!4s[G_PLACE_ID]!12m4!2m3!1i360!2i120!4i8!13m57!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2!1i86!2i86!1m2!1i408!2i240!7m33!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!1m3!1e9!2b1!3e2!2b1!9b0!15m8!1m7!1m2!1m1!1e2!2m2!1i195!2i195!3i20!14m2!1s[SESSION_ID]!7e81!15m112!1m33!13m9!2b1!3b1!4b1!6i1!8b1!9b1!14b1!20b1!25b1!18m22!3b1!4b1!5b1!6b1!9b1!12b1!13b1!14b1!17b1!20b1!21b1!22b1!25b1!27m1!1b0!28b0!30b1!32b1!33m1!1b1!34b1!36e2!10m1!8e3!11m1!3e1!14m1!3b0!17b1!20m2!1e3!1e6!24b1!25b1!26b1!27b1!29b1!30m1!2b1!36b1!37b1!39m3!2m2!2i1!3i1!43b1!52b1!54m1!1b1!55b1!56m1!1b1!61m2!1m1!1e1!65m5!3m4!1m3!1m2!1i224!2i298!72m22!1m8!2b1!5b1!7b1!12m4!1b1!2b1!4m1!1e1!4b1!8m10!1m6!4m1!1e1!4m1!1e3!4m1!1e4!3soth
```

#### `/maps/vt/stream` Endpoint
- **Purpose**: Vector tile data for map rendering and indoor information
- **Parameters**: Complex protobuf encoding with zoom levels, coordinates
- **Response**: Binary protobuf data (up to 1.7MB observed)
- **Content-Type**: `application/vnd.google.octet-stream-compressible`

**Key Parameters Identified**:
- `1i18!2i128746!3i81687!2i7!3x2097151`: Tile coordinates and zoom
- `2m3!1e0!2sm!3i750510260`: Map layer and version info
- Indoor data flags and place ID references

### 2. Data Loading Patterns

#### Initial Page Load
1. Main place page loads with embedded data parameters
2. JavaScript initializes map and triggers data requests
3. `/maps/preview/place` fetches detailed place information
4. Vector tiles load for map rendering

#### Tenant Directory Loading
1. User interaction triggers tenant directory display
2. Dynamic JavaScript requests load tenant data
3. Protobuf-encoded parameters control data scope and pagination
4. Responses contain structured tenant information

### 3. Parameter Encoding Analysis

#### Protobuf Parameter Structure
Google uses a custom protobuf encoding scheme with `!` separators:

```
pb=!1m16!1s[PLACE_ID]!3m8!1m3!1d[DELTA]!2d[LONGITUDE]!3d[LATITUDE]...
```

**Decoded Structure Elements**:
- Place ID: `0x4887c78e6281b45d:0xc4ad4b61a12fde3f`
- Coordinates: Edinburgh St James Quarter (55.9552777, -3.1885505)
- Viewport: `1i1492!2i499` (pixel dimensions)
- Zoom level: `4f13.1`
- Session/context data: Complex nested parameters

### 4. Response Format Analysis

#### JSON Response Structure (Preview/Place)
- Content-Type: `application/json; charset=UTF-8`
- Size: 392,242 bytes (significant data payload)
- Likely contains: place details, tenant listings, metadata

#### Binary Protobuf Responses (VT Stream)
- Content-Type: `application/vnd.google.octet-stream-compressible`
- Size: Up to 1.7MB (large data payloads)
- Contains: Map tiles, indoor data, place information

### 5. Authentication & Session Management

#### Observed Headers
- `authuser=0`: User authentication context
- `x-client-data`: Browser fingerprinting data
- `x-browser-validation`: Browser integrity checks
- `x-maps-diversion-context-bin`: Maps-specific context data

#### Session Tracking
- Session IDs embedded in request parameters
- Context preservation across requests
- State management for pagination and interaction history

## Implementation Strategy Recommendations

### 1. Network Interception Approach
**Recommended**: Use browser automation with HAR capture for initial research, then implement direct API calls with extracted parameters.

**Why**: Direct scraping fails due to:
- Dynamic JavaScript rendering
- Anti-bot measures
- Complex state management
- Protobuf parameter requirements

### 2. Parameter Extraction Strategy
**Required**: Implement protobuf parameter parsing and reconstruction.

**Tools Needed**:
- blackboxprotobuf for schema inference
- HAR file analysis tools
- Parameter extraction and replay capabilities

### 3. Data Flow Understanding
**Critical**: Map the complete data flow from protobuf parameters → network requests → JSON/binary responses → DOM rendering.

### 4. Pagination Strategy
**Required**: Understand infinite scrolling triggers in network requests, not just DOM events.

## Next Steps for Research

1. **Extract Response Bodies**: Need actual JSON/protobuf content from HAR captures
2. **Protobuf Schema Reverse Engineering**: Use blackboxprotobuf on captured data
3. **Parameter Correlation**: Map DOM interactions to network request patterns
4. **Session State Analysis**: Understand context preservation across requests

## Conclusion

Google Maps employs a sophisticated, multi-layered data loading architecture that combines traditional REST endpoints with complex protobuf parameter encoding. Successful scraping requires forensic network analysis and parameter reconstruction rather than simple DOM manipulation.

**Key Success Factors**:
- Complete HAR capture with response bodies
- Protobuf schema understanding
- Parameter extraction and replay capabilities
- Session state management

This analysis provides the foundation for implementing an effective Google Maps scraping solution.
