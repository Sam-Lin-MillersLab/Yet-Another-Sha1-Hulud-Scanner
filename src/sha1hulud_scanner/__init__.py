"""
Shai-Hulud 2.0 Scanner

A CLI tool to detect packages affected by the Shai-Hulud 2.0 supply chain attack
by scanning lock files against a database of known vulnerable packages.
"""

__version__ = "0.1.0"
__author__ = "maxisam"

from .models import (
    LockFileType,
    OutputFormat,
    VulnerablePackage,
    InstalledPackage,
    ScanResult,
    ScanSummary,
)
from .scanner import Scanner

__all__ = [
    "__version__",
    "LockFileType",
    "OutputFormat", 
    "VulnerablePackage",
    "InstalledPackage",
    "ScanResult",
    "ScanSummary",
    "Scanner",
]
