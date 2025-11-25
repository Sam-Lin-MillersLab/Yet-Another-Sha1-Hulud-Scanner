"""
Unit tests for data models.
"""

import pytest
from pathlib import Path
from datetime import datetime, timezone
from sha1hulud_scanner.models import (
    InstalledPackage,
    VulnerablePackage,
    ScanResult,
    ScanSummary,
    LockFileType,
)


class TestInstalledPackage:
    def test_initialization(self):
        """Test valid initialization."""
        pkg = InstalledPackage(
            name="test-pkg",
            version="1.0.0",
            file_path=Path("/tmp/lock"),
            file_type=LockFileType.NPM,
        )
        assert pkg.name == "test-pkg"
        assert pkg.version == "1.0.0"
        assert pkg.file_type == LockFileType.NPM
        assert pkg.key == ("test-pkg", "1.0.0")
        assert str(pkg) == "test-pkg@1.0.0"

    def test_validation(self):
        """Test validation logic."""
        with pytest.raises(ValueError, match="Package name must not be empty"):
            InstalledPackage(
                name="",
                version="1.0.0",
                file_path=Path("/tmp/lock"),
                file_type=LockFileType.NPM,
            )
        
        with pytest.raises(ValueError, match="Package version must not be empty"):
            InstalledPackage(
                name="pkg",
                version="",
                file_path=Path("/tmp/lock"),
                file_type=LockFileType.NPM,
            )


class TestVulnerablePackage:
    def test_initialization(self):
        """Test valid initialization."""
        pkg = VulnerablePackage(
            name="vuln-pkg",
            version="1.2.3",
            source="packages.md",
        )
        assert pkg.name == "vuln-pkg"
        assert pkg.version == "1.2.3"
        assert pkg.source == "packages.md"
        assert pkg.key == ("vuln-pkg", "1.2.3")
        assert str(pkg) == "vuln-pkg@1.2.3"

    def test_validation(self):
        """Test validation logic."""
        with pytest.raises(ValueError, match="Invalid source"):
            VulnerablePackage(
                name="pkg",
                version="1.0.0",
                source="invalid.txt",
            )


class TestScanResult:
    def test_initialization(self):
        """Test valid initialization."""
        result = ScanResult(
            package_name="vuln-pkg",
            installed_version="1.2.3",
            vulnerable_versions=["1.2.3", "1.2.4"],
            file_path=Path("/tmp/lock"),
            file_type=LockFileType.YARN,
        )
        assert result.package_name == "vuln-pkg"
        assert result.installed_version == "1.2.3"
        assert len(result.vulnerable_versions) == 2
        assert str(result) == "vuln-pkg@1.2.3"


class TestScanSummary:
    def test_initialization(self):
        """Test valid initialization and methods."""
        summary = ScanSummary(
            scan_date=datetime.now(timezone.utc),
            target_path=Path("/tmp"),
        )
        assert summary.files_scanned == 0
        assert summary.vulnerabilities_found == 0
        assert not summary.has_vulnerabilities
        
        # Add result
        result = ScanResult(
            package_name="vuln-pkg",
            installed_version="1.2.3",
            vulnerable_versions=["1.2.3"],
            file_path=Path("/tmp/lock"),
            file_type=LockFileType.NPM,
        )
        summary.add_result(result)
        
        assert summary.vulnerabilities_found == 1
        assert summary.has_vulnerabilities
        assert len(summary.vulnerabilities) == 1
        
        # Add warning
        summary.add_warning("Test warning")
        assert len(summary.warnings) == 1
        
        # Increment files
        summary.increment_files_scanned()
        assert summary.files_scanned == 1
