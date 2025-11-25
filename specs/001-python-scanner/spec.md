# Feature Specification: Python Shai-Hulud 2.0 Scanner

**Feature Branch**: `001-python-scanner`  
**Created**: 2025-11-25  
**Status**: Draft  
**Input**: User description: "Create a python scanner to scan all frontend package lock files (yarn.lock, package-lock.json, etc) against packages.md and wiz-packages.csv to detect Shai-Hulud 2.0 Supply Chain Attack affected packages"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Scan Single Lock File (Priority: P1)

As a security engineer, I want to scan a single package lock file against the known vulnerable packages list so that I can quickly identify if my project is affected by the Shai-Hulud 2.0 supply chain attack.

**Why this priority**: This is the core functionality - without the ability to scan a single file, the tool provides no value. This enables immediate detection of vulnerable packages.

**Independent Test**: Can be fully tested by providing a single `package-lock.json` or `yarn.lock` file and verifying the scanner outputs correct matches against the known vulnerable packages database.

**Acceptance Scenarios**:

1. **Given** a valid `package-lock.json` file and the vulnerable packages database, **When** the scanner processes the file, **Then** it outputs a list of any matching vulnerable packages with their versions.
2. **Given** a valid `yarn.lock` file and the vulnerable packages database, **When** the scanner processes the file, **Then** it outputs a list of any matching vulnerable packages with their versions.
3. **Given** a lock file with no vulnerable packages, **When** the scanner processes the file, **Then** it outputs a message indicating no vulnerabilities found.
4. **Given** an invalid or malformed lock file, **When** the scanner attempts to process it, **Then** it displays a clear error message without crashing.

---

### User Story 2 - Scan Directory Recursively (Priority: P2)

As a security engineer managing multiple projects, I want to scan an entire directory tree for all package lock files so that I can audit multiple projects or a monorepo in a single command.

**Why this priority**: This extends the core functionality to handle real-world scenarios where projects contain multiple packages or users want to audit entire codebases.

**Independent Test**: Can be fully tested by running the scanner on a directory containing multiple nested projects with various lock files and verifying all are discovered and scanned.

**Acceptance Scenarios**:

1. **Given** a directory containing multiple `package-lock.json` and `yarn.lock` files in nested subdirectories, **When** the scanner runs with the directory path, **Then** it discovers and scans all lock files, reporting results for each.
2. **Given** a directory with no lock files, **When** the scanner runs, **Then** it reports that no lock files were found.
3. **Given** a directory path that doesn't exist, **When** the scanner attempts to scan, **Then** it displays a clear error message.

---

### User Story 3 - Support Multiple Lock File Formats (Priority: P2)

As a developer using different package managers, I want the scanner to support `package-lock.json` (npm), `yarn.lock` (Yarn v1 and v2+), and `pnpm-lock.yaml` (pnpm) so that I can use the tool regardless of my package manager choice.

**Why this priority**: Different teams use different package managers, and supporting all major formats ensures broad adoption and utility.

**Independent Test**: Can be tested by providing sample lock files from each format and verifying correct parsing and vulnerability detection for each.

**Acceptance Scenarios**:

1. **Given** a `package-lock.json` file (npm), **When** the scanner processes it, **Then** it correctly extracts package names and versions.
2. **Given** a `yarn.lock` file (Yarn v1 format), **When** the scanner processes it, **Then** it correctly extracts package names and versions.
3. **Given** a `pnpm-lock.yaml` file, **When** the scanner processes it, **Then** it correctly extracts package names and versions.

---

### User Story 4 - Generate Actionable Output Report (Priority: P3)

As a security team lead, I want the scanner to produce a clear, structured report (console output and optional file export) so that I can share findings with stakeholders and track remediation.

**Why this priority**: Reporting enhances usability but the core scanning functionality delivers primary value even with basic console output.

**Independent Test**: Can be tested by running a scan and verifying the output format is readable and contains all necessary information (package name, installed version, vulnerable versions, file location).

**Acceptance Scenarios**:

1. **Given** a scan that finds vulnerabilities, **When** results are displayed, **Then** each finding shows: package name, installed version, vulnerable version(s) from database, and file path.
2. **Given** a completed scan, **When** the user requests JSON output format, **Then** the scanner outputs machine-readable JSON.
3. **Given** a completed scan, **When** the user specifies an output file path, **Then** results are written to that file.

---

### Edge Cases

- What happens when a lock file contains the same package at multiple versions? → Report each match separately with location
- How does the system handle lock files with corrupted or incomplete entries? → Skip with warning, continue scanning
- What happens when the vulnerable packages database (packages.md or wiz-packages.csv) is missing or inaccessible?
- How does the scanner handle scoped packages (e.g., `@babel/core`) vs unscoped packages?
- What happens when version specifiers in the database use ranges (e.g., `= 1.0.1 || = 1.0.2`)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST parse and load the vulnerable packages database from both `packages.md` and `wiz-packages.csv` files
- **FR-002**: System MUST parse `package-lock.json` files (npm lockfile format v1, v2, and v3)
- **FR-003**: System MUST parse `yarn.lock` files (Yarn v1 classic format)
- **FR-004**: System MUST parse `pnpm-lock.yaml` files (pnpm lockfile format)
- **FR-005**: System MUST match installed packages against the vulnerable packages database using exact package name and version matching
- **FR-006**: System MUST support recursive directory scanning to find all lock files
- **FR-007**: System MUST output findings to the console with package name, version, and source file
- **FR-008**: System MUST provide a command-line interface with arguments for: file/directory path, output format, output file path, verbose mode flag, and optional custom database path
- **FR-009**: System MUST handle scoped npm packages (packages starting with `@`)
- **FR-010**: System MUST support multiple affected versions per package (as seen in the CSV format with `||` separators)
- **FR-011**: System MUST exit with a non-zero exit code when vulnerabilities are found (for CI/CD integration)
- **FR-012**: System MUST provide clear error messages for invalid inputs or missing files
- **FR-013**: System MUST skip malformed lock file entries with a warning message and continue scanning remaining entries
- **FR-014**: System MUST report each vulnerable package instance separately when the same package appears at multiple versions in a lock file

### Key Entities *(include if feature involves data)*

- **VulnerablePackage**: Represents a known compromised package with its name and affected version(s) from the Shai-Hulud 2.0 attack database
- **InstalledPackage**: Represents a package found in a lock file with its name, version, and source file location
- **ScanResult**: Represents the outcome of scanning a lock file, containing matched vulnerable packages and metadata
- **LockFile**: Represents a parseable package lock file with its type (npm, yarn, pnpm), path, and parsed package contents

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Scanner correctly identifies 100% of packages in test lock files that match entries in the vulnerable packages database
- **SC-002**: Scanner processes a typical lock file (500+ packages) in under 5 seconds
- **SC-003**: Scanner produces zero false positives - only reports exact matches against the database
- **SC-004**: Scanner can scan a monorepo with 50+ lock files in under 60 seconds
- **SC-005**: Scanner integrates with CI/CD pipelines by providing appropriate exit codes (0 = no issues, non-zero = vulnerabilities found)
- **SC-006**: Users can understand scanner output without consulting documentation - output is self-explanatory

## Clarifications

### Session 2025-11-25

- Q: Should the scanner provide verbose/debug logging output? → A: Verbose logging via optional CLI flag
- Q: How should the scanner handle malformed lock file entries? → A: Skip malformed entries with warning, continue scanning
- Q: How should matches be reported when same package exists at multiple versions? → A: Report each version match separately with location context
- Q: Should the scanner require internet or work offline? → A: Work fully offline with bundled database
- Q: Should the scanner support custom database path or only bundled? → A: Support optional custom database path via CLI flag

## Assumptions

- The vulnerable packages database files (`packages.md` and `wiz-packages.csv`) are bundled with the scanner in the `data/` directory
- Scanner operates fully offline with no internet connectivity required
- Version matching is exact (no semver range matching needed) - a package is vulnerable only if its exact version appears in the database
- The scanner is run in environments with Python 3.8+ installed
- Lock files are well-formed according to their respective package manager specifications
- The CSV format uses `= X.Y.Z` prefix for versions and `||` as separator for multiple versions
