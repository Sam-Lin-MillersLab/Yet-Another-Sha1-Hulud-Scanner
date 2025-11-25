"""
Data models for the Shai-Hulud 2.0 Scanner.

This module exports all model classes and enumerations used throughout the scanner.
"""

from enum import Enum


class LockFileType(Enum):
    """Enumeration of supported lock file types."""
    NPM = "package-lock.json"
    YARN = "yarn.lock"
    PNPM = "pnpm-lock.yaml"


class OutputFormat(Enum):
    """Enumeration of supported output formats."""
    CONSOLE = "console"
    JSON = "json"


# Import model classes for re-export
from .vulnerable_package import VulnerablePackage
from .installed_package import InstalledPackage
from .scan_result import ScanResult, ScanSummary

__all__ = [
    "LockFileType",
    "OutputFormat",
    "VulnerablePackage",
    "InstalledPackage",
    "ScanResult",
    "ScanSummary",
]
