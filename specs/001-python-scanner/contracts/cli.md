# CLI Interface Contract

**Feature**: 001-python-scanner | **Date**: 2025-11-25

## Command

```bash
sha1hulud-scanner [OPTIONS] <PATH>
# or
python -m sha1hulud_scanner [OPTIONS] <PATH>
```

## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `PATH` | string | Yes | File or directory path to scan |

## Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--output` | `-o` | string | - | Output file path (writes results to file) |
| `--format` | `-f` | enum | console | Output format: `console` or `json` |
| `--verbose` | `-v` | flag | false | Enable verbose/debug logging |
| `--db-path` | `-d` | string | bundled | Custom path to vulnerable packages database directory |
| `--help` | `-h` | flag | - | Show help message |
| `--version` | | flag | - | Show version information |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - no vulnerabilities found |
| 1 | Vulnerabilities found |
| 2 | Error - invalid arguments, missing files, etc. |

## Usage Examples

### Scan a single file

```bash
sha1hulud-scanner ./package-lock.json
```

### Scan a directory recursively

```bash
sha1hulud-scanner ./my-project
```

### JSON output to file

```bash
sha1hulud-scanner -f json -o results.json ./my-project
```

### Verbose mode with custom database

```bash
sha1hulud-scanner -v -d ./custom-db ./my-project
```

### CI/CD integration

```bash
sha1hulud-scanner ./my-project || exit 1
```

## Output Specifications

### Console Format (default)

```
🔍 Scanning: /path/to/target

⚠️  VULNERABLE PACKAGES FOUND

  📦 @posthog/icons@0.36.1
     └── Found in: package-lock.json
     └── Path: /path/to/package-lock.json
  
  📦 lodash@4.17.21
     └── Found in: yarn.lock
     └── Path: /path/to/yarn.lock

────────────────────────────────────────
Summary: 2 vulnerable packages found
Files scanned: 3
────────────────────────────────────────
```

### Console Format (no vulnerabilities)

```
🔍 Scanning: /path/to/target

✅ No vulnerable packages found

────────────────────────────────────────
Summary: 0 vulnerable packages found
Files scanned: 5
────────────────────────────────────────
```

### JSON Format

```json
{
  "scan_date": "2025-11-25T12:00:00Z",
  "target_path": "/path/to/target",
  "files_scanned": 3,
  "vulnerabilities_found": 2,
  "results": [
    {
      "package": "@posthog/icons",
      "version": "0.36.1",
      "file_type": "package-lock.json",
      "file_path": "/path/to/package-lock.json"
    },
    {
      "package": "lodash",
      "version": "4.17.21",
      "file_type": "yarn.lock",
      "file_path": "/path/to/yarn.lock"
    }
  ],
  "warnings": []
}
```

### Verbose Output (stderr)

```
[DEBUG] Loading database from: /path/to/data
[DEBUG] Loaded 1093 vulnerable package entries from packages.md
[DEBUG] Loaded 799 vulnerable package entries from wiz-packages.csv
[DEBUG] Total unique vulnerable packages: 1100
[DEBUG] Discovering lock files in: /path/to/target
[DEBUG] Found: /path/to/package-lock.json
[DEBUG] Found: /path/to/subdir/yarn.lock
[DEBUG] Parsing: /path/to/package-lock.json (npm lockfileVersion: 3)
[DEBUG] Extracted 523 packages from package-lock.json
[WARN] Skipping malformed entry at line 145: invalid version format
[DEBUG] Matching packages against database...
[DEBUG] Found match: @posthog/icons@0.36.1
```

## Error Messages

| Scenario | Message | Exit Code |
|----------|---------|-----------|
| Path not found | `Error: Path not found: {path}` | 2 |
| No lock files found | `No lock files found in: {path}` | 0 |
| Database not found | `Error: Vulnerable packages database not found at: {path}` | 2 |
| Invalid format option | `Error: Invalid format '{value}'. Use 'console' or 'json'` | 2 |
| Permission denied | `Error: Permission denied: {path}` | 2 |
