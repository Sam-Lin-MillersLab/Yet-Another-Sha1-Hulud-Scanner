"""
VulnerablePackage model representing a known compromised package.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class VulnerablePackage:
    """
    Represents a known compromised package from the Shai-Hulud 2.0 attack database.
    
    Attributes:
        name: Package name (with scope if applicable, e.g., "@posthog/icons")
        version: Affected version string
        source: Database source file ("packages.md" or "wiz-packages.csv")
    
    The (name, version) tuple forms a unique identifier for vulnerable packages.
    """
    name: str
    version: str
    source: str
    
    def __post_init__(self) -> None:
        """Validate required fields."""
        if not self.name or not self.name.strip():
            raise ValueError("Package name must not be empty")
        if not self.version or not self.version.strip():
            raise ValueError("Package version must not be empty")
        if self.source not in ("packages.md", "wiz-packages.csv"):
            raise ValueError(f"Invalid source: {self.source}")
    
    @property
    def key(self) -> tuple[str, str]:
        """Return the unique identifier tuple (name, version)."""
        return (self.name, self.version)
    
    def __str__(self) -> str:
        """Return human-readable representation."""
        return f"{self.name}@{self.version}"
