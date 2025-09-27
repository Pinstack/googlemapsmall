# Research Findings: Google Maps Mall Scraping POC

**Research Date**: 2025-09-27
**Methodology**: Forensic network analysis + HAR file examination
**Scope**: St James Quarter mall tenant data extraction

## Executive Summary

Google Maps employs a sophisticated multi-layered architecture for mall tenant data that combines dynamic JavaScript rendering with protobuf-encoded network requests. Direct DOM scraping is insufficient due to anti-bot measures and complex state management. A hybrid approach using network analysis and controlled browser automation is required.

## Key Research Findings

### 1. Google Maps Network Architecture

#### Primary Endpoints Identified
- **`/maps/preview/place`**: Main place data endpoint (JSON, ~392KB responses)
- **`/maps/vt/stream`**: Vector tile streaming (binary protobuf, up to 1.7MB)
- **`/maps/_/js/`**: Dynamic JavaScript loading with obfuscated code

#### Parameter Encoding Scheme
Google uses a custom protobuf encoding with `!` separators:
```
pb=!1m16!1s[PLACE_ID]!3m8!1m3!1d[DELTA]!2d[LONGITUDE]!3d[LATITUDE]!3m2!1i1492!2i499!4f13.1
```

**Decoded Elements**:
- Place ID: `0x4887c78e6281b45d:0xc4ad4b61a12fde3f`
- Coordinates: Edinburgh St James Quarter (55.9552777, -3.1885505)
- Viewport dimensions and zoom levels
- Session state and context preservation

### 2. Data Loading Patterns

#### Initial Page Load Sequence
1. HTML page loads with embedded JavaScript
2. Maps API initializes with authentication (`authuser=0`)
3. Place data requests trigger via JavaScript events
4. Protobuf parameters constructed dynamically
5. Network requests made with complex headers

#### Tenant Directory Access
- **"View All" Method**: Single comprehensive request for all tenants
- **Category Method**: Separate requests per category with pagination
- **Infinite Scrolling**: Network requests triggered by scroll events
- **State Management**: Session context maintained across requests

### 3. Authentication & Session Management

#### Headers Observed
- `x-client-data`: Browser fingerprinting data (base64 encoded)
- `x-browser-validation`: Browser integrity validation
- `x-maps-diversion-context-bin`: Maps-specific session context
- `user-agent`: Standard browser identification

#### Session Persistence
- Session IDs embedded in protobuf parameters
- Context preservation across pagination requests
- State recovery mechanisms for interrupted sessions

### 4. Response Format Analysis

#### JSON Responses (`/maps/preview/place`)
- Content-Type: `application/json; charset=UTF-8`
- Size: 392,242 bytes (comprehensive place data)
- Structure: Hierarchical place information with tenant listings

#### Binary Protobuf Responses (`/maps/vt/stream`)
- Content-Type: `application/vnd.google.octet-stream-compressible`
- Size: Variable (up to 1.7MB for complex tiles)
- Purpose: Map rendering data and indoor venue information

### 5. Technical Constraints & Challenges

#### Anti-Bot Measures
- Dynamic JavaScript rendering prevents simple HTTP requests
- Browser fingerprinting and validation
- Rate limiting and request throttling
- Session state validation

#### Schema Evolution
- Protobuf schemas change without notice
- Parameter structures may evolve
- Response formats subject to modification
- Backward compatibility not guaranteed

## Implementation Strategy Recommendations

### Decision: Hybrid Network Analysis + Controlled Browser Automation
**Rationale**: Pure scraping fails due to dynamic JavaScript and anti-bot measures. Pure API reverse engineering is too complex for POC scope. Hybrid approach leverages forensic insights for efficient automation.

**Why Chosen**:
- Network analysis provides understanding of data flows
- Browser automation handles dynamic interactions
- Protobuf parameter reconstruction enables reliable requests
- Balances implementation complexity with effectiveness

### Alternatives Considered

#### Alternative 1: Pure DOM Scraping
- **Rejected**: Fails due to dynamic JavaScript rendering and anti-bot measures
- **Issues**: Unreliable selectors, timing dependencies, detection risk

#### Alternative 2: Full API Reverse Engineering
- **Rejected for POC**: Too complex, requires extensive protobuf schema documentation
- **Better for**: Production systems with long-term maintenance

#### Alternative 3: Selenium WebDriver Only
- **Rejected**: Slower, more detectable, higher maintenance overhead
- **Playwright Preferred**: Better performance, modern async support, comprehensive browser control

### Technology Stack Validation

#### blackboxprotobuf
- **Purpose**: Automated protobuf schema inference and decoding
- **Fit**: Essential for understanding Google Maps data structures
- **Validation**: Successfully used for similar reverse engineering tasks

#### Playwright
- **Purpose**: Controlled browser automation with network interception
- **Fit**: Handles dynamic JavaScript while allowing HAR capture
- **Validation**: Superior to Selenium for modern web scraping

#### pytest
- **Purpose**: TDD approach with comprehensive test coverage
- **Fit**: Enables test-first development with HAR fixtures
- **Validation**: Industry standard for Python testing

## Success Factors

### Critical Success Factors
1. **Complete HAR Capture**: Must capture all network interactions
2. **Protobuf Understanding**: Schema inference must work reliably
3. **Session Management**: Proper context preservation across requests
4. **Error Handling**: Robust handling of network failures and schema changes

### Risk Mitigation
1. **Fallback Strategies**: DOM scraping as backup when network approach fails
2. **Monitoring**: Comprehensive logging of success/failure patterns
3. **Testing**: Extensive test coverage for different scenarios
4. **Documentation**: Detailed forensic research enables future maintenance

## Next Steps

1. **Implement HAR Analysis Module**: Process captured network data
2. **Develop Protobuf Handler**: Decode and reconstruct parameters
3. **Build Controlled Scraper**: Use Playwright with network insights
4. **Create Test Suite**: Validate all components with HAR fixtures

## Conclusion

The forensic research reveals that Google Maps mall scraping requires a sophisticated hybrid approach combining network analysis with controlled browser automation. The protobuf parameter encoding and dynamic JavaScript rendering make simple scraping approaches ineffective. However, the research provides a clear path forward for implementing an effective POC scraper.

**Confidence Level**: High - Network patterns are well-understood, implementation approach is validated through research.
