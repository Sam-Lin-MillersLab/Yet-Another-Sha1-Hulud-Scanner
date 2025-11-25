"""
Unit tests for the Scanner class.
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from sha1hulud_scanner.scanner import Scanner
from sha1hulud_scanner.models import InstalledPackage, LockFileType


class TestScanner:
    @pytest.fixture
    def mock_db_parser(self):
        with patch("sha1hulud_scanner.scanner.DatabaseParser") as MockParser:
            instance = MockParser.return_value
            # Mock load_all to return some vulnerable packages
            instance.load_all.return_value = (
                {("vuln-pkg", "1.0.0")},
                {"vuln-pkg": ["1.0.0"]}
            )
            yield instance

    def test_initialization(self, mock_db_parser, tmp_path):
        """Test scanner initialization."""
        scanner = Scanner(tmp_path)
        assert scanner.db_path == tmp_path
        mock_db_parser.load_all.assert_called_once()

    def test_match_packages(self, mock_db_parser, tmp_path):
        """Test matching packages against database."""
        scanner = Scanner(tmp_path)
        
        packages = [
            InstalledPackage("vuln-pkg", "1.0.0", Path("lock"), LockFileType.NPM),
            InstalledPackage("safe-pkg", "2.0.0", Path("lock"), LockFileType.NPM),
        ]
        
        results = scanner.match_packages(packages)
        
        assert len(results) == 1
        assert results[0].package_name == "vuln-pkg"
        assert results[0].installed_version == "1.0.0"

    def test_scan_file_not_found(self, mock_db_parser, tmp_path):
        """Test scanning a non-existent file."""
        scanner = Scanner(tmp_path)
        summary = scanner.scan_file(tmp_path / "nonexistent")
        
        assert not summary.has_vulnerabilities
        assert len(summary.warnings) > 0
        assert "File not found" in summary.warnings[0]

    def test_scan_file_no_parser(self, mock_db_parser, tmp_path):
        """Test scanning a file with no matching parser."""
        scanner = Scanner(tmp_path)
        unknown_file = tmp_path / "unknown.txt"
        unknown_file.touch()
        
        summary = scanner.scan_file(unknown_file)
        
        assert not summary.has_vulnerabilities
        assert len(summary.warnings) > 0
        assert "No parser available" in summary.warnings[0]

    def test_scan_directory(self, mock_db_parser, tmp_path):
        """Test scanning a directory."""
        scanner = Scanner(tmp_path)
        
        # Create a dummy lock file
        lock_file = tmp_path / "package-lock.json"
        lock_file.write_text("{}", encoding="utf-8")
        
        # Mock the parser to return a vulnerable package
        with patch.object(scanner, "_get_parser_for_file") as mock_get_parser:
            mock_parser = MagicMock()
            mock_parser.parse.return_value = [
                InstalledPackage("vuln-pkg", "1.0.0", lock_file, LockFileType.NPM)
            ]
            mock_get_parser.return_value = mock_parser
            
            summary = scanner.scan_directory(tmp_path)
            
            assert summary.files_scanned == 1
            assert summary.vulnerabilities_found == 1
            assert summary.vulnerabilities[0].package_name == "vuln-pkg"

    def test_discover_lock_files(self, mock_db_parser, tmp_path):
        """Test lock file discovery."""
        scanner = Scanner(tmp_path)
        
        # Create structure:
        # /package-lock.json
        # /src/yarn.lock
        # /node_modules/pnpm-lock.yaml (should be ignored)
        
        (tmp_path / "package-lock.json").touch()
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "yarn.lock").touch()
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "pnpm-lock.yaml").touch()
        
        lock_files = scanner.discover_lock_files(tmp_path)
        
        assert len(lock_files) == 2
        names = {f.name for f in lock_files}
        assert "package-lock.json" in names
        assert "yarn.lock" in names
        assert "pnpm-lock.yaml" not in names
