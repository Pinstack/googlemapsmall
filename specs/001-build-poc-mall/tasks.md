# Tasks: POC Mall Scraper for Google Maps

**Input**: Design documents from `/specs/001-build-poc-mall/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: HAR analyzer, protobuf handler, scraper, data processor
   → Integration: component connections, error handling, logging
   → Polish: performance testing, docs, final validation
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- Paths assume single project structure per plan.md

## Phase 3.1: Setup
- [x] T001 Create project structure per implementation plan (src/, tests/ directories)
- [x] T002 Initialize Python 3.11 project with blackboxprotobuf, playwright, pytest, requests dependencies
- [x] T003 [P] Configure linting and formatting tools (flake8, black, vulture)
- [x] T004 [P] Set up test fixtures for HAR data and protobuf schemas

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T005 [P] Contract test HAR analysis in tests/contract/test_har_analysis.py
- [x] T006 [P] Contract test protobuf handler in tests/contract/test_protobuf_handler.py
- [x] T007 [P] Contract test browser automation in tests/contract/test_browser_automation.py
- [ ] T008 [P] Integration test mall directory scraping in tests/integration/test_mall_scraping.py
- [ ] T009 [P] Integration test protobuf decoding in tests/integration/test_protobuf_decoding.py
- [x] T010 [P] Unit test data validation in tests/unit/test_data_validation.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [x] T011 [P] HAR analyzer module in src/har_analyzer.py
- [x] T012 [P] Protobuf handler module in src/protobuf_handler.py
- [x] T013 [P] Browser automation scraper in src/scraper.py
- [x] T014 [P] Data processor module in src/data_processor.py
- [x] T015 [P] CLI interface in src/cli.py
- [x] T016 [P] Configuration management in src/config.py

## Phase 3.4: Integration
- [x] T017 Connect HAR analyzer to protobuf handler for parameter extraction
- [x] T018 Integrate scraper with HAR analyzer for network-aware automation
- [ ] T019 Connect data processor to scraper for brand extraction and validation
- [ ] T020 Add comprehensive error handling and retry logic
- [ ] T021 Implement logging and progress tracking throughout pipeline
- [ ] T022 Add session management for Google Maps authentication context

## Phase 3.5: Polish
- [ ] T023 [P] Performance tests for <2 minute execution in tests/performance/test_execution_time.py
- [ ] T024 [P] Memory usage tests under 500MB in tests/performance/test_memory_usage.py
- [x] T025 [P] Anti-bot detection tests in tests/integration/test_anti_bot.py
- [ ] T026 [P] Update README.md with usage instructions and examples
- [ ] T027 [P] Add comprehensive docstrings and type hints throughout codebase
- [ ] T028 Run complete POC validation against quickstart.md success criteria
- [ ] T029 Final code review and cleanup (remove debug code, optimize imports)

## Dependencies
- Tests (T005-T010) before implementation (T011-T016)
- T011 blocks T017 (HAR analyzer needed for integration)
- T013 blocks T018 (scraper needed for HAR integration)
- T014 blocks T019 (data processor needed for scraper integration)
- Implementation (T011-T022) before polish (T023-T029)
- T017-T022 can run in parallel after core modules (T011-T016) complete

## Parallel Example
```
# Launch T005-T007 together (contract tests):
Task: "Contract test HAR analysis in tests/contract/test_har_analysis.py"
Task: "Contract test protobuf handler in tests/contract/test_protobuf_handler.py"
Task: "Contract test browser automation in tests/contract/test_browser_automation.py"

# Launch T011-T016 together (core modules):
Task: "HAR analyzer module in src/har_analyzer.py"
Task: "Protobuf handler module in src/protobuf_handler.py"
Task: "Browser automation scraper in src/scraper.py"
Task: "Data processor module in src/data_processor.py"
Task: "CLI interface in src/cli.py"
Task: "Configuration management in src/config.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing (TDD requirement)
- Commit after each task completion
- Avoid: vague tasks, same file conflicts, over-engineering

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - Each contract file → contract test task [P]
   - contracts/har-analysis-contract.md → T005
   - contracts/protobuf-handler-contract.md → T006
   - contracts/browser-automation-contract.md → T007

2. **From Data Model**:
   - Each entity → validation/model task [P]
   - Brand entity → T010 (data validation tests)
   - NetworkRequest entity → HAR analyzer integration

3. **From User Stories**:
   - Each acceptance scenario → integration test [P]
   - Scenario 1 → T008 (mall directory scraping)
   - Scenario 2 → T009 (protobuf decoding)

4. **From Quickstart**:
   - Validation checklist → final polish tasks
   - Performance metrics → performance tests (T023-T024)

5. **Ordering**:
   - Setup → Tests → Core → Integration → Polish
   - Dependencies prevent parallel execution where files overlap
   - TDD enforced: tests before corresponding implementation

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests (3 contracts → 3 test tasks)
- [x] All entities have model/validation tasks (5 entities → integrated into modules)
- [x] All tests come before implementation (T005-T010 before T011-T016)
- [x] Parallel tasks truly independent (different files, no shared state)
- [x] Each task specifies exact file path (all tasks have explicit paths)
- [x] No task modifies same file as another [P] task (verified file separation)
