
# Implementation Plan: POC Mall Scraper for Google Maps

**Branch**: `001-build-poc-mall` | **Date**: 2025-09-27 | **Spec**: specs/001-build-poc-mall/spec.md
**Input**: Feature specification from specs/001-build-poc-mall/spec.md

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Build a POC scraper to extract ~150 brands from St James Quarter mall using network analysis and protobuf parameter reconstruction. Leverage forensic research insights to implement efficient programmatic data extraction with comprehensive testing and modular architecture.

## Technical Context
**Language/Version**: Python 3.11 (for protobuf handling and data processing)
**Primary Dependencies**: blackboxprotobuf, playwright, pytest, requests
**Storage**: JSON files for extracted tenant data, HAR files for network analysis
**Testing**: pytest with fixtures for HAR data and protobuf schemas
**Target Platform**: Linux/macOS development environment
**Project Type**: Single project (CLI tool for data extraction)
**Performance Goals**: <2 minutes for complete mall scraping (POC validation)
**Constraints**: Network-dependent, Google Maps ToS compliance, protobuf schema evolution
**Scale/Scope**: Single mall POC (~150 brands), expandable to multiple malls

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Test-First Compliance
- [x] All planned features have defined test scenarios (HAR analysis, scraping, data validation)
- [x] pytest fixtures prepared for static test data (HAR fixtures, protobuf schemas)
- [x] TDD approach documented in implementation strategy (tests before implementation)

### API-First Design
- [x] Network analysis approach replaces traditional API-first (protobuf parameter reconstruction)
- [x] RESTful design principles applied to Google Maps endpoints analysis
- [x] Contract testing strategy defined for Google Maps API interactions

### Performance & Scalability
- [x] Performance budgets defined (<2 minutes for POC validation, vs <500ms for production)
- [x] Horizontal scaling not required for single mall POC
- [x] CDN strategy not applicable (direct API calls)

### Data Privacy & Security
- [x] GDPR compliance measures planned (location data handling in POC scope)
- [x] Location data handling strategy defined (JSON export with privacy considerations)
- [x] Security audit requirements identified (network traffic analysis)

### Lean Architecture
- [x] DRY principles applied in design (reusable HAR analysis, protobuf handling)
- [x] YAGNI approach validated (only implement what's needed for ~150 brand POC)
- [x] Modular design enabling independent testing (HAR analysis, scraping, data processing)

## Project Structure

### Documentation (this feature)
```
specs/001-build-poc-mall/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
├── forensic-report.md   # Phase 1A/1B output (completed)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
src/
├── har_analyzer.py       # HAR file processing and protobuf extraction
├── scraper.py           # Main scraping logic with browser automation
├── protobuf_handler.py  # blackboxprotobuf schema management
├── data_processor.py    # Tenant data extraction and validation
├── cli.py              # Command-line interface
└── config.py           # Configuration management

tests/
├── fixtures/           # HAR files, protobuf schemas, test data
├── unit/              # Unit tests for each module
├── integration/       # End-to-end scraping tests
└── contract/          # API contract validation tests
```

**Structure Decision**: Single project CLI tool structure selected for Google Maps scraping POC. Modular architecture with separate concerns for HAR analysis, scraping, protobuf handling, and data processing. Test structure follows pytest conventions with fixtures for HAR data and protobuf schemas.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - All technical context is defined (no NEEDS CLARIFICATION remaining)
   - Dependencies identified: blackboxprotobuf, playwright, pytest, requests
   - Integration patterns: HAR analysis, protobuf decoding, browser automation

2. **Generate and dispatch research agents**:
   ```
   Research completed via forensic analysis:
     - Google Maps network architecture documented
     - Protobuf parameter structures mapped
     - Browser automation patterns identified
   Technology choices validated:
     - blackboxprotobuf for schema inference
     - playwright for controlled browser automation
     - pytest for TDD approach
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: Hybrid network analysis + scraping approach
   - Rationale: Direct scraping fails due to dynamic JS; network analysis enables targeted extraction
   - Alternatives considered: Pure DOM scraping (rejected), API reverse engineering (too complex for POC)

**Output**: research.md with forensic research synthesis

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Brand entity with name, category, location details
   - Category entity for tenant grouping
   - Mall entity for location context
   - Network request entities for HAR data structures

2. **Generate API contracts** from functional requirements:
   - HAR processing contract for network analysis
   - Protobuf decoding contract for data structures
   - Browser automation contract for scraping
   - Output contract specifications to `/contracts/`

3. **Generate contract tests** from contracts:
   - HAR analysis contract tests
   - Protobuf schema validation tests
   - Browser automation contract tests
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Mall directory navigation scenarios
   - Tenant data extraction validation
   - Network analysis verification
   - Quickstart test = complete POC validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh cursor`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - Add Google Maps scraping context and forensic research insights
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, .cursor context file

## Phase 1 Execution Results
*Phase 1 completed successfully - all artifacts generated*

**Phase 1 Outputs Created**:
- ✅ research.md: Forensic research findings and implementation strategy
- ✅ data-model.md: Entity definitions and relationships
- ✅ contracts/: HAR analysis, protobuf handler, browser automation contracts
- ✅ quickstart.md: POC execution guide with troubleshooting
- ✅ .cursor context: Updated with Google Maps scraping insights

**Constitution Check Results**:
- ✅ All principles validated for POC scope
- ✅ Performance adapted for <2 minutes target
- ✅ Security scope limited to POC data handling
- ✅ Lean architecture confirmed for modular design

## Phase 2: Task Planning Approach
*Ready for /tasks command execution*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P]
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:
- TDD order: Tests before implementation
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/tasks command)
- [x] Phase 3: Tasks generated (/tasks command)
- [x] Phase 4: Implementation complete
- [x] Phase 5: Validation passed (including real-world testing)

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Real-world testing completed
- [x] Anti-bot protection documented
- [x] Legal/ethical assessment completed
- [ ] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
