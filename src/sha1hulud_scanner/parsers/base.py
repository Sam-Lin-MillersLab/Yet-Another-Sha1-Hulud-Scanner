"""
Abstract base class for lock file parsers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from ..models import InstalledPackage, LockFileType


class BaseLockFileParser(ABC):
    """
    Abstract base class for lock file parsers.
    
    Subclasses must implement the parse() method to extract installed packages
    from their specific lock file format.
    """
    
    @property
    @abstractmethod
    def file_type(self) -> LockFileType:
        """Return the lock file type this parser handles."""
        pass
    
    @property
    @abstractmethod
    def filename(self) -> str:
        """Return the filename this parser handles (e.g., 'package-lock.json')."""
        pass
    
    @abstractmethod
    def parse(self, file_path: Path) -> List[InstalledPackage]:
        """
        Parse a lock file and extract installed packages.
        
        Args:
            file_path: Path to the lock file to parse
            
        Returns:
            List of InstalledPackage objects found in the lock file
            
        Raises:
            FileNotFoundError: If the lock file doesn't exist
            ValueError: If the lock file is malformed
        """
        pass
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Check if this parser can handle the given file.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if this parser can handle the file, False otherwise
        """
        return file_path.name == self.filename
