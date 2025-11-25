# Shai-Hulud 2.0 Scanner

A command-line tool to detect packages affected by the Shai-Hulud 2.0 supply chain attack by scanning package lock files against a database of known vulnerable packages.

## Features

- 🔍 **Multi-format support**: Scans `package-lock.json` (npm), `yarn.lock` (Yarn v1), and `pnpm-lock.yaml` (pnpm)
- 📁 **Recursive scanning**: Scan entire directory trees for all lock files
- 🔌 **Offline operation**: Works completely offline with bundled vulnerability database
- 📊 **Multiple output formats**: Human-readable console output or machine-readable JSON
- 🚀 **CI/CD ready**: Exit codes designed for pipeline integration

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/maxisam/Yet-Another-Sha1-Hulud-Scanner.git
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

### GitHub Actions

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
    - pip install -e .
    - sha1hulud-scanner .
  allow_failure: false
```

## Example Output

### Console Output (Vulnerabilities Found)

```
🔍 Scanning: ./my-project

⚠️  VULNERABLE PACKAGES FOUND

  📦 @posthog/icons@0.36.1
     └── Found in: package-lock.json
     └── Path: ./my-project/package-lock.json

────────────────────────────────────────
Summary: 1 vulnerable packages found
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
  "warnings": []
}
```

## What is Shai-Hulud 2.0?

The Shai-Hulud 2.0 attack is a supply chain attack targeting npm packages. This scanner checks your project's dependencies against a database of known compromised package versions to identify if you're affected.

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=sha1hulud_scanner
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
