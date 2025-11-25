"""
ScanResult and ScanSummary models for scan output.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from . import LockFileType


@dataclass
class ScanResult:
    """
    Represents a vulnerability match found during scanning.
    
    Attributes:
        package_name: Name of the matched package
        installed_version: Version found in the lock file
        vulnerable_versions: List of all vulnerable versions from the database
        file_path: Path to the lock file where the package was found
        file_type: Type of lock file (NPM, YARN, or PNPM)
    """
    package_name: str
    installed_version: str
    vulnerable_versions: List[str]
    file_path: Path
    file_type: "LockFileType"
    
    def __post_init__(self) -> None:
        """Validate required fields."""
        if not self.package_name or not self.package_name.strip():
            raise ValueError("Package name must not be empty")
        if not self.installed_version or not self.installed_version.strip():
            raise ValueError("Installed version must not be empty")
        if not self.vulnerable_versions:
            raise ValueError("Vulnerable versions list must not be empty")
    
    def __str__(self) -> str:
        """Return human-readable representation."""
        return f"{self.package_name}@{self.installed_version}"


@dataclass
class ScanSummary:
    """
    Aggregates results from a complete scan operation.
    
    Attributes:
        scan_date: UTC timestamp when scan was performed
        target_path: The file or directory that was scanned
        files_scanned: Number of lock files processed
        vulnerabilities: List of all vulnerability matches found
        warnings: List of warning messages (e.g., malformed entries skipped)
    """
    scan_date: datetime
    target_path: Path
    files_scanned: int = 0
    vulnerabilities: List[ScanResult] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def vulnerabilities_found(self) -> int:
        """Return the count of vulnerabilities found."""
        return len(self.vulnerabilities)
    
    @property
    def has_vulnerabilities(self) -> bool:
        """Return True if any vulnerabilities were found."""
        return len(self.vulnerabilities) > 0
    
    def add_result(self, result: ScanResult) -> None:
        """Add a scan result to the summary."""
        self.vulnerabilities.append(result)
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message to the summary."""
        self.warnings.append(warning)
    
    def increment_files_scanned(self) -> None:
        """Increment the files scanned counter."""
        self.files_scanned += 1
