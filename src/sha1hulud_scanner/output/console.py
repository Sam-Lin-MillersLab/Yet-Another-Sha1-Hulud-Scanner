"""
Console output formatter for human-readable scan results.
"""

import sys
from typing import TextIO

from ..models import ScanSummary


class ConsoleOutput:
    """
    Formatter for human-readable console output.
    """
    
    def __init__(self, stream: TextIO = None) -> None:
        """
        Initialize console output formatter.
        
        Args:
            stream: Output stream (defaults to stdout)
        """
        self.stream = stream or sys.stdout
    
    def format(self, summary: ScanSummary) -> None:
        """
        Format and output scan results to console.
        
        Args:
            summary: Scan summary to format
        """
        self._print(f"\n🔍 Scanning: {summary.target_path}\n")
        
        if summary.has_vulnerabilities:
            self._print_vulnerabilities(summary)
        else:
            self._print_clean(summary)
        
        # Print version mismatch warnings (affected packages with different versions)
        if summary.has_version_mismatch_warnings:
            self._print_version_mismatch_warnings(summary)
        
        self._print_summary(summary)
        
        # Print general warnings if any
        if summary.warnings:
            self._print("\nWarnings:")
            for warning in summary.warnings:
                self._print(f"  ⚠️  {warning}")
    
    def _print_vulnerabilities(self, summary: ScanSummary) -> None:
        """Print vulnerability findings."""
        self._print("🚨 VULNERABLE PACKAGES FOUND\n")
        
        for result in summary.vulnerabilities:
            self._print(f"  📦 {result.package_name}@{result.installed_version}")
            self._print(f"     └── Found in: {result.file_type.value}")
            self._print(f"     └── Path: {result.file_path}")
            self._print("")
    
    def _print_version_mismatch_warnings(self, summary: ScanSummary) -> None:
        """Print warnings for packages matching affected names but with different versions."""
        self._print("⚠️  AFFECTED PACKAGES WITH DIFFERENT VERSIONS\n")
        self._print("   The following packages are in the affected package list,")
        self._print("   but your installed version differs from known vulnerable versions.\n")
        
        for warning in summary.version_mismatch_warnings:
            self._print(f"  📦 {warning.package_name}@{warning.installed_version}")
            self._print(f"     └── Known vulnerable versions: {', '.join(warning.known_vulnerable_versions)}")
            self._print(f"     └── Found in: {warning.file_type.value}")
            self._print(f"     └── Path: {warning.file_path}")
            self._print("")
    
    def _print_clean(self, summary: ScanSummary) -> None:
        """Print clean scan message."""
        self._print("✅ No vulnerable packages found\n")
    
    def _print_summary(self, summary: ScanSummary) -> None:
        """Print scan summary."""
        separator = "─" * 40
        self._print(separator)
        self._print(f"Summary: {summary.vulnerabilities_found} vulnerable packages found")
        if summary.has_version_mismatch_warnings:
            self._print(f"         {len(summary.version_mismatch_warnings)} affected packages with different versions")
        self._print(f"Files scanned: {summary.files_scanned}")
        self._print(separator)
    
    def _print(self, message: str) -> None:
        """Print a message to the output stream."""
        print(message, file=self.stream)
