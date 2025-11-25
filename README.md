# Shai-Hulud 2.0 Scanner

A command-line tool to detect packages affected by the Shai-Hulud 2.0 supply chain attack by scanning package lock files against a database of known vulnerable packages.

## Features

- 🔍 **Multi-format support**: Scans `package-lock.json` (npm), `yarn.lock` (Yarn v1), and `pnpm-lock.yaml` (pnpm)
- 📁 **Recursive scanning**: Scan entire directory trees for all lock files
- 🔌 **Offline operation**: Works completely offline with bundled vulnerability database
- ⚠️ **Version mismatch warnings**: Alerts when packages match affected names but have different versions
- 📊 **Multiple output formats**: Human-readable console output or machine-readable JSON
- 🚀 **CI/CD ready**: Exit codes designed for pipeline integration

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/Sam-Lin-MillersLab/Yet-Another-Sha1-Hulud-Scanner.git
cd Yet-Another-Sha1-Hulud-Scanner

# Install dependencies and sync
uv sync

# Run the scanner
uv run sha1hulud-scanner ./my-project
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/Sam-Lin-MillersLab/Yet-Another-Sha1-Hulud-Scanner.git
cd Yet-Another-Sha1-Hulud-Scanner

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

### Requirements

- Python 3.8 or higher
- PyYAML >= 6.0

## Usage

### Basic Usage

```bash
# Scan a single lock file
sha1hulud-scanner ./package-lock.json

# Scan a directory recursively
sha1hulud-scanner ./my-project

# Scan with verbose output
sha1hulud-scanner -v ./my-project
```

### Output Formats

```bash
# Default console output
sha1hulud-scanner ./my-project

# JSON output
sha1hulud-scanner -f json ./my-project

# Save results to file
sha1hulud-scanner -f json -o results.json ./my-project
```

### Custom Database Path

```bash
# Use a custom vulnerability database
sha1hulud-scanner -d /path/to/custom/database ./my-project
```

### CLI Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output` | `-o` | Output file path |
| `--format` | `-f` | Output format: `console` (default) or `json` |
| `--verbose` | `-v` | Enable verbose logging |
| `--db-path` | `-d` | Custom database directory path |
| `--version` | | Show version number |
| `--help` | `-h` | Show help message |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - no vulnerabilities found |
| 1 | Vulnerabilities found |
| 2 | Error - invalid arguments, missing files, etc. |

## CI/CD Integration

### GitHub Actions (with uv)

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v4

- name: Scan for Shai-Hulud vulnerabilities
  run: |
    uv sync
    uv run sha1hulud-scanner . || exit 1
```

### GitHub Actions (with pip)

```yaml
- name: Scan for Shai-Hulud vulnerabilities
  run: |
    pip install -e .
    sha1hulud-scanner . || exit 1
```

### GitLab CI

```yaml
security_scan:
  script:
    - pip install uv
    - uv sync
    - uv run sha1hulud-scanner .
  allow_failure: false
```

## Example Output

### Console Output (Vulnerabilities Found)

```
🔍 Scanning: ./my-project

🚨 VULNERABLE PACKAGES FOUND

  📦 @posthog/icons@0.36.1
     └── Found in: package-lock.json
     └── Path: ./my-project/package-lock.json

⚠️  AFFECTED PACKAGES WITH DIFFERENT VERSIONS

   The following packages are in the affected package list,
   but your installed version differs from known vulnerable versions.

  📦 @accordproject/concerto-analysis@3.25.0
     └── Known vulnerable versions: 3.24.1
     └── Found in: package-lock.json
     └── Path: ./my-project/package-lock.json

────────────────────────────────────────
Summary: 1 vulnerable packages found
         1 affected packages with different versions
Files scanned: 3
────────────────────────────────────────
```

### Console Output (Clean)

```
🔍 Scanning: ./my-project

✅ No vulnerable packages found

────────────────────────────────────────
Summary: 0 vulnerable packages found
Files scanned: 3
────────────────────────────────────────
```

### JSON Output

```json
{
  "scan_date": "2025-11-25T12:00:00+00:00",
  "target_path": "./my-project",
  "files_scanned": 3,
  "vulnerabilities_found": 1,
  "results": [
    {
      "package": "@posthog/icons",
      "version": "0.36.1",
      "file_type": "package-lock.json",
      "file_path": "./my-project/package-lock.json"
    }
  ],
  "version_mismatch_warnings": [
    {
      "package": "@accordproject/concerto-analysis",
      "installed_version": "3.25.0",
      "known_vulnerable_versions": ["3.24.1"],
      "file_type": "package-lock.json",
      "file_path": "./my-project/package-lock.json"
    }
  ],
  "warnings": []
}
```

## What is Shai-Hulud 2.0?

The Shai-Hulud 2.0 attack is a supply chain attack targeting npm packages. This scanner checks your project's dependencies against a database of known compromised package versions to identify if you're affected.

## Development

### Running Tests

```bash
# Using uv (recommended)
uv sync
uv run pytest

# Run tests with coverage
uv run pytest --cov=sha1hulud_scanner

# Using pip
pip install -e ".[dev]"
pytest
```

### Project Structure

```
src/sha1hulud_scanner/
├── __init__.py          # Package initialization
├── __main__.py          # Module entry point
├── cli.py               # CLI implementation
├── scanner.py           # Core scanning logic
├── models/              # Data models
├── parsers/             # Lock file parsers
└── output/              # Output formatters
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
