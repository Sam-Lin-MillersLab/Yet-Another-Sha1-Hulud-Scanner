# Research: Python Shai-Hulud 2.0 Scanner

**Feature**: 001-python-scanner | **Date**: 2025-11-25

## Database Format Analysis

### packages.md Format

**Decision**: Parse as markdown list with `- package@version` format

**Rationale**: Each line follows pattern `- {package_name}@{version}`. Scoped packages use `@scope/name@version`. Simple regex or string split parsing.

**Format Examples**:
```
- 02-echo@0.0.7
- @accordproject/concerto-analysis@3.24.1
- @alexcolls/nuxt-socket.io@0.0.7
```

**Parsing Strategy**: 
1. Read file line by line
2. Match pattern `^- (.+)@([0-9].*)$`
3. For scoped packages, handle `@scope/name@version` by splitting from the last `@`

### wiz-packages.csv Format

**Decision**: Parse as CSV with header row, handle `||` version separators

**Rationale**: Standard CSV with `Package,Version` columns. Version field uses `= X.Y.Z` prefix and `||` as OR separator for multiple versions.

**Format Examples**:
```csv
Package,Version
02-echo,= 0.0.7
@alexcolls/nuxt-socket.io,= 0.0.7 || = 0.0.8
```

**Parsing Strategy**:
1. Use Python `csv` module (stdlib)
2. Skip header row
3. Split version field by `||`, strip `= ` prefix from each
4. Create entry for each package+version combination

## Lock File Format Analysis

### package-lock.json (npm)

**Decision**: Use `json` module (stdlib) for parsing

**Rationale**: Standard JSON format. Support lockfileVersion 1, 2, and 3.

**Format Differences**:
- **v1**: Packages in `dependencies` object with nested structure
- **v2/v3**: Packages in `packages` object with flat `node_modules/` paths

**Parsing Strategy**:
1. Load JSON with stdlib
2. Check `lockfileVersion` field
3. For v1: recursively traverse `dependencies`
4. For v2/v3: iterate `packages` object, extract package name from path

### yarn.lock (Yarn v1 Classic)

**Decision**: Custom parser for YAML-like format

**Rationale**: yarn.lock is NOT valid YAML. It uses a custom format with quoted package specifiers.

**Format Example**:
```
"@babel/core@^7.0.0":
  version "7.12.3"
  resolved "https://..."
  
lodash@^4.17.0, lodash@^4.17.21:
  version "4.17.21"
```

**Parsing Strategy**:
1. Parse line by line
2. Detect package entry lines (end with `:` and contain `@` version specifier)
3. Find `version "X.Y.Z"` line following entry
4. Handle multiple package specifiers on same line (comma-separated)

**Alternatives Considered**:
- `@yarnpkg/lockfile` npm package (rejected: requires Node.js)
- Generic YAML parser (rejected: yarn.lock not valid YAML)

### pnpm-lock.yaml

**Decision**: Use PyYAML for parsing

**Rationale**: Valid YAML format. Packages under `packages` key with path-based keys.

**Format Example**:
```yaml
packages:
  /@babel/core@7.12.3:
    resolution: {integrity: sha512-...}
    dependencies:
      ...
```

**Parsing Strategy**:
1. Load with PyYAML
2. Iterate `packages` dictionary
3. Extract package name and version from key (format: `/@scope/name@version` or `/name@version`)

## Dependency Decisions

### Required Dependencies

| Package | Version | Rationale |
|---------|---------|-----------|
| PyYAML | >=6.0 | pnpm-lock.yaml parsing (widely used, stable) |

### Stdlib Usage

| Module | Purpose |
|--------|---------|
| `argparse` | CLI argument parsing |
| `json` | package-lock.json parsing |
| `csv` | wiz-packages.csv parsing |
| `pathlib` | Cross-platform path handling |
| `dataclasses` | Model definitions |
| `re` | Regex for packages.md and yarn.lock parsing |
| `logging` | Verbose mode output |
| `sys` | Exit codes |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | >=7.0 | Test framework |
| pytest-cov | >=4.0 | Coverage reporting |

## Performance Considerations

**Decision**: Use set-based lookups for vulnerability matching

**Rationale**: With ~1100 vulnerable packages, O(1) set membership testing is optimal vs O(n) list scanning.

**Implementation**:
```python
# Build lookup set: {("package-name", "1.0.0"), ...}
vulnerable_set: Set[Tuple[str, str]] = set()

# O(1) lookup per installed package
is_vulnerable = (pkg_name, pkg_version) in vulnerable_set
```

## Error Handling Strategy

**Decision**: Graceful degradation with warnings

**Rationale**: Per clarification, skip malformed entries with warning, continue scanning.

**Implementation**:
- Wrap individual entry parsing in try/except
- Log warning with entry details
- Continue processing remaining entries
- Track warning count in scan results

## Output Format Design

### Console Output (Human-Readable)

```
🔍 Scanning: /path/to/project

⚠️  VULNERABLE PACKAGES FOUND

  📦 @posthog/icons@0.36.1
     └── Found in: package-lock.json
     └── Vulnerable version(s): 0.36.1
  
  📦 lodash@4.17.21
     └── Found in: yarn.lock
     └── Vulnerable version(s): 4.17.21

Summary: 2 vulnerable packages found in 3 files scanned
```

### JSON Output

```json
{
  "scan_date": "2025-11-25T12:00:00Z",
  "files_scanned": 3,
  "vulnerabilities_found": 2,
  "results": [
    {
      "package": "@posthog/icons",
      "version": "0.36.1",
      "file": "package-lock.json",
      "file_path": "/path/to/package-lock.json"
    }
  ]
}
```
