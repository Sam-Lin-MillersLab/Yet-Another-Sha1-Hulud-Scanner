"""
InstalledPackage model representing a package found in a lock file.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import LockFileType


@dataclass(frozen=True)
class InstalledPackage:
    """
    Represents a package found in a lock file.
    
    Attributes:
        name: Package name (with scope if applicable, e.g., "@babel/core")
        version: Installed version string
        file_path: Absolute path to the lock file where this package was found
        file_type: Type of lock file (NPM, YARN, or PNPM)
    """
    name: str
    version: str
    file_path: Path
    file_type: "LockFileType"
    
    def __post_init__(self) -> None:
        """Validate required fields."""
        if not self.name or not self.name.strip():
            raise ValueError("Package name must not be empty")
        if not self.version or not self.version.strip():
            raise ValueError("Package version must not be empty")
    
    @property
    def key(self) -> tuple[str, str]:
        """Return the identifier tuple (name, version) for matching."""
        return (self.name, self.version)
    
    def __str__(self) -> str:
        """Return human-readable representation."""
        return f"{self.name}@{self.version}"
