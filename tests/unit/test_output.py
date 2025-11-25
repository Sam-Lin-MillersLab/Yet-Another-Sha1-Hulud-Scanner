"""
Unit tests for output formatters.
"""

import json
import io
from datetime import datetime, timezone
from pathlib import Path
from sha1hulud_scanner.output import ConsoleOutput, JsonOutput
from sha1hulud_scanner.models import (
    ScanSummary,
    ScanResult,
    LockFileType,
)


class TestConsoleOutput:
    def test_format_clean(self):
        """Test formatting a clean scan."""
        summary = ScanSummary(
            scan_date=datetime.now(timezone.utc),
            target_path=Path("/tmp"),
            files_scanned=5,
        )
        
        stream = io.StringIO()
        formatter = ConsoleOutput(stream=stream)
        formatter.format(summary)
        
        output = stream.getvalue()
        assert "No vulnerable packages found" in output
        assert "Files scanned: 5" in output

    def test_format_vulnerable(self):
        """Test formatting a scan with vulnerabilities."""
        summary = ScanSummary(
            scan_date=datetime.now(timezone.utc),
            target_path=Path("/tmp"),
            files_scanned=5,
        )
        
        result = ScanResult(
            package_name="vuln-pkg",
            installed_version="1.0.0",
            vulnerable_versions=["1.0.0"],
            file_path=Path("/tmp/lock"),
            file_type=LockFileType.NPM,
        )
        summary.add_result(result)
        
        stream = io.StringIO()
        formatter = ConsoleOutput(stream=stream)
        formatter.format(summary)
        
        output = stream.getvalue()
        assert "VULNERABLE PACKAGES FOUND" in output
        assert "vuln-pkg@1.0.0" in output
        assert "Files scanned: 5" in output
        assert "1 vulnerable packages found" in output


class TestJsonOutput:
    def test_format(self):
        """Test JSON formatting."""
        summary = ScanSummary(
            scan_date=datetime.now(timezone.utc),
            target_path=Path("/tmp"),
            files_scanned=5,
        )
        
        result = ScanResult(
            package_name="vuln-pkg",
            installed_version="1.0.0",
            vulnerable_versions=["1.0.0"],
            file_path=Path("/tmp/lock"),
            file_type=LockFileType.NPM,
        )
        summary.add_result(result)
        summary.add_warning("Test warning")
        
        formatter = JsonOutput()
        json_str = formatter.format(summary)
        
        data = json.loads(json_str)
        assert data["files_scanned"] == 5
        assert data["vulnerabilities_found"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["package"] == "vuln-pkg"
        assert data["results"][0]["version"] == "1.0.0"
        assert len(data["warnings"]) == 1
