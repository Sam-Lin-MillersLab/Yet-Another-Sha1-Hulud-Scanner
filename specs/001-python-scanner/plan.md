# Implementation Plan: Python Shai-Hulud 2.0 Scanner

**Branch**: `001-python-scanner` | **Date**: 2025-11-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-python-scanner/spec.md`

## Summary

Build a Python CLI scanner that detects packages affected by the Shai-Hulud 2.0 supply chain attack by comparing lock files (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`) against the bundled vulnerable packages database (`packages.md` and `wiz-packages.csv`). The scanner works fully offline, supports recursive directory scanning, and provides human-readable and JSON output formats suitable for CI/CD integration.

## Technical Context

**Language/Version**: Python 3.8+ (for broad compatibility)  
**Primary Dependencies**: PyYAML (for pnpm-lock.yaml parsing), argparse (stdlib for CLI)  
**Storage**: File-based (bundled CSV and MD database files in `data/` directory)  
**Testing**: pytest with pytest-cov for coverage  
**Target Platform**: Cross-platform CLI (Windows, macOS, Linux)  
**Project Type**: Single CLI application  
**Performance Goals**: Process 500+ packages in <5 seconds; 50+ lock files in <60 seconds  
**Constraints**: Fully offline, no network dependencies, minimal external packages  
**Scale/Scope**: ~1100 vulnerable package entries, typical lock files with 100-2000 packages

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution is a template without specific rules. Applying general best practices:

| Principle | Status | Notes |
|-----------|--------|-------|
| Self-contained library | ✅ PASS | Scanner is standalone with bundled data |
| CLI Interface | ✅ PASS | Text in/out via CLI with JSON support |
| Test coverage | ✅ PLANNED | pytest with unit and integration tests |
| Simplicity | ✅ PASS | Minimal dependencies, single-purpose tool |

## Project Structure

### Documentation (this feature)

```text
specs/001-python-scanner/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI interface contract)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── __main__.py          # Entry point for `python -m sha1hulud_scanner`
├── cli.py               # CLI argument parsing and main orchestration
├── models/
│   ├── __init__.py
│   ├── vulnerable_package.py   # VulnerablePackage dataclass
│   ├── installed_package.py    # InstalledPackage dataclass
│   └── scan_result.py          # ScanResult dataclass
├── parsers/
│   ├── __init__.py
│   ├── base.py                 # Abstract base parser
│   ├── database_parser.py      # Parse packages.md and wiz-packages.csv
│   ├── npm_parser.py           # Parse package-lock.json
│   ├── yarn_parser.py          # Parse yarn.lock
│   └── pnpm_parser.py          # Parse pnpm-lock.yaml
├── scanner.py           # Core scanning logic
└── output/
    ├── __init__.py
    ├── console.py              # Human-readable console output
    └── json_output.py          # JSON output formatter

tests/
├── __init__.py
├── conftest.py                 # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_database_parser.py
│   ├── test_npm_parser.py
│   ├── test_yarn_parser.py
│   ├── test_pnpm_parser.py
│   └── test_scanner.py
├── integration/
│   ├── __init__.py
│   ├── test_cli.py
│   └── test_full_scan.py
└── fixtures/
    ├── sample_package_lock.json
    ├── sample_yarn.lock
    ├── sample_pnpm_lock.yaml
    └── sample_vulnerable_db/

data/                           # Existing - bundled vulnerable packages database
├── packages.md
└── wiz-packages.csv

pyproject.toml                  # Project configuration
README.md                       # Usage documentation
```

**Structure Decision**: Single project structure selected. This is a standalone CLI tool without web/mobile components. The `src/` layout separates concerns: models for data structures, parsers for file format handling, scanner for matching logic, and output for formatting.

## Complexity Tracking

> No constitution violations - design follows simplicity principles.
