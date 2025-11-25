# Tasks: Python Shai-Hulud 2.0 Scanner

**Input**: Design documents from `/specs/001-python-scanner/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md

**Tests**: Not explicitly requested in specification - minimal test coverage for critical parsing logic only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure per plan.md in src/
- [ ] T002 Create pyproject.toml with project metadata, dependencies (PyYAML>=6.0, pytest>=7.0, pytest-cov>=4.0), and `[project.scripts]` entry point: `sha1hulud-scanner = "sha1hulud_scanner.cli:main"`
- [ ] T003 [P] Create src/__init__.py with package version
- [ ] T004 [P] Create src/__main__.py entry point for `python -m sha1hulud_scanner`
- [ ] T005 [P] Create tests/__init__.py and tests/conftest.py with shared fixtures

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create LockFileType and OutputFormat enums in src/models/__init__.py
- [ ] T007 [P] Create VulnerablePackage dataclass in src/models/vulnerable_package.py
- [ ] T008 [P] Create InstalledPackage dataclass in src/models/installed_package.py
- [ ] T009 [P] Create ScanResult dataclass in src/models/scan_result.py
- [ ] T010 Create ScanSummary dataclass in src/models/scan_result.py (depends on T009)
- [ ] T011 [P] Create abstract BaseLockFileParser in src/parsers/base.py
- [ ] T012 Implement DatabaseParser for packages.md and wiz-packages.csv in src/parsers/database_parser.py; include FileNotFoundError handling with clear error message per FR-012
- [ ] T013 [P] Create tests/fixtures/ directory with sample vulnerable database files

**Checkpoint**: Foundation ready - database can be loaded, models defined

---

## Phase 3: User Story 1 - Scan Single Lock File (Priority: P1) 🎯 MVP

**Goal**: Scan a single package-lock.json or yarn.lock file and detect vulnerable packages

**Independent Test**: Run scanner on a single lock file, verify correct matches output

### Implementation for User Story 1

- [ ] T014 [P] [US1] Implement NpmParser for package-lock.json (v1, v2, v3) in src/parsers/npm_parser.py
- [ ] T015 [P] [US1] Implement YarnParser for yarn.lock (v1 format) in src/parsers/yarn_parser.py
- [ ] T016 [US1] Implement Scanner class with match_packages() method in src/scanner.py
- [ ] T017 [US1] Implement ConsoleOutput formatter in src/output/console.py
- [ ] T018 [US1] Implement basic CLI with single file scanning in src/cli.py
- [ ] T019 [P] [US1] Create tests/fixtures/sample_package_lock.json with known vulnerable packages
- [ ] T020 [P] [US1] Create tests/fixtures/sample_yarn.lock with known vulnerable packages
- [ ] T021 [US1] Add error handling for malformed lock file entries (skip with warning)

**Checkpoint**: Scanner can process single npm/yarn lock files and report vulnerabilities

---

## Phase 4: User Story 2 - Scan Directory Recursively (Priority: P2)

**Goal**: Scan entire directory tree for all lock files

**Independent Test**: Run scanner on directory with nested lock files, verify all discovered and scanned

### Implementation for User Story 2

- [ ] T022 [US2] Implement discover_lock_files() method in src/scanner.py for recursive file discovery
- [ ] T023 [US2] Update CLI to detect file vs directory path and route appropriately in src/cli.py
- [ ] T024 [US2] Handle "no lock files found" case with appropriate message
- [ ] T025 [US2] Aggregate results from multiple lock files into single ScanSummary

**Checkpoint**: Scanner can process directories recursively, finding all lock files

---

## Phase 5: User Story 3 - Support Multiple Lock File Formats (Priority: P2)

**Goal**: Add pnpm-lock.yaml support

**Independent Test**: Run scanner on pnpm-lock.yaml, verify correct package extraction

### Implementation for User Story 3

- [ ] T026 [US3] Implement PnpmParser for pnpm-lock.yaml in src/parsers/pnpm_parser.py
- [ ] T027 [US3] Register PnpmParser in scanner's file type detection in src/scanner.py
- [ ] T028 [P] [US3] Create tests/fixtures/sample_pnpm_lock.yaml with known vulnerable packages

**Checkpoint**: Scanner supports all three lock file formats (npm, yarn, pnpm)

---

## Phase 6: User Story 4 - Generate Actionable Output Report (Priority: P3)

**Goal**: JSON output and file export options

**Independent Test**: Run scanner with --format json, verify valid JSON output

### Implementation for User Story 4

- [ ] T029 [US4] Implement JsonOutput formatter in src/output/json_output.py
- [ ] T030 [US4] Add --format and --output CLI options in src/cli.py
- [ ] T031 [US4] Implement file output writing with error handling
- [ ] T032 [US4] Add verbose logging support with --verbose flag in src/cli.py
- [ ] T033 [US4] Add --db-path option for custom database location in src/cli.py

**Checkpoint**: Scanner supports JSON output, file export, verbose mode, custom DB path

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final integration and documentation

- [ ] T034 [P] Implement proper exit codes (0=clean, 1=vulnerabilities, 2=error) in src/cli.py
- [ ] T035 [P] Add --version flag to CLI
- [ ] T036 [P] Create README.md with installation and usage instructions
- [ ] T037 Run quickstart.md validation - test all documented commands work
- [ ] T038 [P] Add .gitignore for Python project (venv, __pycache__, .pytest_cache, etc.)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories should proceed sequentially: P1 → P2 → P2 → P3
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Core MVP functionality
- **User Story 2 (P2)**: Depends on US1 (single file scanning) - Extends to directories
- **User Story 3 (P2)**: Can start after Foundational - Independent parser (can parallel with US2)
- **User Story 4 (P3)**: Depends on US1 - Extends output capabilities

### Within Each Phase

- Models before services
- Parsers before scanner
- Scanner before CLI
- Core implementation before error handling

### Parallel Opportunities

```
Phase 1 - All [P] tasks in parallel:
  T003, T004, T005

Phase 2 - Models in parallel:
  T007, T008, T009 (then T010)
  T011, T012, T013 in parallel after models

Phase 3 (US1) - Parsers in parallel:
  T014, T015 (then T016 → T017 → T018)
  T019, T020 (fixtures) in parallel with implementation

Phase 5 (US3) - Can run in parallel with Phase 4 (US2):
  T026, T027, T028

Phase 7 - All [P] tasks in parallel:
  T034, T035, T036, T038
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T013)
3. Complete Phase 3: User Story 1 (T014-T021)
4. **STOP and VALIDATE**: Test with real lock files
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test → MVP ready!
3. Add User Story 2 → Test → Directory scanning works
4. Add User Story 3 → Test → All formats supported
5. Add User Story 4 → Test → Full feature set

---

## Task Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| Setup | T001-T005 | Project structure, dependencies |
| Foundational | T006-T013 | Models, enums, base parser, database parser |
| US1 (P1) | T014-T021 | Single file scanning (npm, yarn) |
| US2 (P2) | T022-T025 | Recursive directory scanning |
| US3 (P2) | T026-T028 | pnpm support |
| US4 (P3) | T029-T033 | JSON output, file export, verbose, custom DB |
| Polish | T034-T038 | Exit codes, version, README, validation |

**Total Tasks**: 38
**Parallel Opportunities**: 15 tasks can run in parallel at various points
