# Data Model: Python Shai-Hulud 2.0 Scanner

**Feature**: 001-python-scanner | **Date**: 2025-11-25

## Entity Definitions

### VulnerablePackage

Represents a known compromised package from the Shai-Hulud 2.0 attack database.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| name | str | Package name (with scope if applicable) | Required, non-empty |
| version | str | Affected version | Required, semver format |
| source | str | Database source file | "packages.md" or "wiz-packages.csv" |

**Uniqueness**: (name, version) tuple

**Examples**:
```python
VulnerablePackage(name="@posthog/icons", version="0.36.1", source="packages.md")
VulnerablePackage(name="lodash", version="4.17.21", source="wiz-packages.csv")
```

---

### InstalledPackage

Represents a package found in a lock file.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| name | str | Package name (with scope if applicable) | Required, non-empty |
| version | str | Installed version | Required |
| file_path | Path | Absolute path to lock file | Required, valid path |
| file_type | LockFileType | Type of lock file | Enum: NPM, YARN, PNPM |

**Examples**:
```python
InstalledPackage(
    name="@babel/core",
    version="7.12.3",
    file_path=Path("/project/package-lock.json"),
    file_type=LockFileType.NPM
)
```

---

### ScanResult

Represents a vulnerability match found during scanning.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| package_name | str | Matched package name | Required |
| installed_version | str | Version found in lock file | Required |
| vulnerable_versions | List[str] | All vulnerable versions from DB | Non-empty list |
| file_path | Path | Lock file where found | Required |
| file_type | LockFileType | Type of lock file | Enum value |

**Examples**:
```python
ScanResult(
    package_name="@posthog/icons",
    installed_version="0.36.1",
    vulnerable_versions=["0.36.1"],
    file_path=Path("/project/package-lock.json"),
    file_type=LockFileType.NPM
)
```

---

### ScanSummary

Aggregates results from a complete scan operation.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| scan_date | datetime | When scan was performed | Required, UTC |
| target_path | Path | Scanned file or directory | Required |
| files_scanned | int | Number of lock files processed | >= 0 |
| vulnerabilities | List[ScanResult] | All matches found | May be empty |
| warnings | List[str] | Parse warnings encountered | May be empty |
| exit_code | int | CLI exit code | 0 = clean, 1 = vulnerabilities |

---

## Enumerations

### LockFileType

```python
class LockFileType(Enum):
    NPM = "package-lock.json"
    YARN = "yarn.lock"
    PNPM = "pnpm-lock.yaml"
```

### OutputFormat

```python
class OutputFormat(Enum):
    CONSOLE = "console"
    JSON = "json"
```

---

## Relationships

```
┌─────────────────────┐
│ VulnerablePackage   │
│ (from database)     │
└─────────┬───────────┘
          │ matches (name, version)
          ▼
┌─────────────────────┐      ┌─────────────────┐
│ InstalledPackage    │──────│ ScanResult      │
│ (from lock file)    │      │ (match found)   │
└─────────────────────┘      └────────┬────────┘
                                      │ aggregates
                                      ▼
                             ┌─────────────────┐
                             │ ScanSummary     │
                             │ (final output)  │
                             └─────────────────┘
```

---

## State Transitions

### Scan Lifecycle

```
[Start] 
   │
   ▼
[Load Database] ──error──▶ [Exit with Error]
   │
   ▼
[Discover Lock Files]
   │
   ├── none found ──▶ [Report: No files found] ──▶ [Exit 0]
   │
   ▼
[Parse Lock Files] 
   │
   ├── parse error ──▶ [Log Warning] ──▶ [Continue]
   │
   ▼
[Match Against Database]
   │
   ▼
[Generate Output]
   │
   ├── vulnerabilities ──▶ [Exit 1]
   │
   └── clean ──▶ [Exit 0]
```

---

## Validation Rules

| Entity | Field | Rule |
|--------|-------|------|
| VulnerablePackage | name | Must not be empty or whitespace-only |
| VulnerablePackage | version | Must match semver-like pattern |
| InstalledPackage | file_path | Must exist and be readable |
| ScanResult | vulnerable_versions | Must contain at least one version |
| ScanSummary | files_scanned | Must equal actual files processed |
