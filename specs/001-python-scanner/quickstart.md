# Quickstart: Shai-Hulud 2.0 Scanner

**Feature**: 001-python-scanner | **Date**: 2025-11-25

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/maxisam/Yet-Another-Sha1-Hulud-Scanner.git
cd Yet-Another-Sha1-Hulud-Scanner

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Requirements

- Python 3.8 or higher
- PyYAML >= 6.0

## Quick Usage

### Scan a Single Project

```bash
# Scan a directory for vulnerable packages
sha1hulud-scanner /path/to/your/project

# Or use Python module directly
python -m sha1hulud_scanner /path/to/your/project
```

### Scan a Specific Lock File

```bash
sha1hulud-scanner ./package-lock.json
sha1hulud-scanner ./yarn.lock
sha1hulud-scanner ./pnpm-lock.yaml
```

### Get JSON Output for CI/CD

```bash
sha1hulud-scanner -f json -o scan-results.json ./my-project

# Check exit code
echo $?  # 0 = clean, 1 = vulnerabilities found
```

## Understanding Output

### Clean Scan

```
🔍 Scanning: ./my-project

✅ No vulnerable packages found

────────────────────────────────────────
Summary: 0 vulnerable packages found
Files scanned: 2
────────────────────────────────────────
```

### Vulnerabilities Found

```
🔍 Scanning: ./my-project

⚠️  VULNERABLE PACKAGES FOUND

  📦 @posthog/icons@0.36.1
     └── Found in: package-lock.json
     └── Path: ./my-project/package-lock.json

────────────────────────────────────────
Summary: 1 vulnerable packages found
Files scanned: 2
────────────────────────────────────────
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Scan for Shai-Hulud vulnerabilities
  run: |
    pip install sha1hulud-scanner
    sha1hulud-scanner . || exit 1
```

### GitLab CI

```yaml
security_scan:
  script:
    - pip install sha1hulud-scanner
    - sha1hulud-scanner .
  allow_failure: false
```

## What is Shai-Hulud 2.0?

The Shai-Hulud 2.0 attack is a supply chain attack targeting npm packages. This scanner checks your project's dependencies against a database of known compromised package versions to identify if you're affected.

## Next Steps

1. Run the scanner on your projects
2. Review any vulnerabilities found
3. Update affected packages to safe versions
4. Add scanning to your CI/CD pipeline
