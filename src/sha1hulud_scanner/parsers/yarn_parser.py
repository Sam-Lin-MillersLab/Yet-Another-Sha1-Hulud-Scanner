"""
Parser for Yarn v1 yarn.lock files.
"""

import logging
import re
from pathlib import Path
from typing import List, Optional

from ..models import InstalledPackage, LockFileType
from .base import BaseLockFileParser

logger = logging.getLogger(__name__)


class YarnParser(BaseLockFileParser):
    """
    Parser for Yarn v1 (Classic) yarn.lock files.
    
    Note: yarn.lock is NOT valid YAML. It uses a custom format.
    """
    
    # Pattern to match package entry lines
    # Examples:
    #   "@babel/core@^7.0.0":
    #   lodash@^4.17.0, lodash@^4.17.21:
    #   "lodash@^4.17.0", "lodash@^4.17.21":
    ENTRY_PATTERN = re.compile(r'^["\']?(@?[^@\s"\']+)@[^:]+["\']?(?:,\s*["\']?@?[^@\s"\']+@[^:]+["\']?)*:\s*$')
    
    # Pattern to extract version from the entry
    VERSION_PATTERN = re.compile(r'^\s+version\s+"([^"]+)"')
    
    @property
    def file_type(self) -> LockFileType:
        return LockFileType.YARN
    
    @property
    def filename(self) -> str:
        return "yarn.lock"
    
    def parse(self, file_path: Path) -> List[InstalledPackage]:
        """
        Parse a yarn.lock file and extract installed packages.
        
        Args:
            file_path: Path to the yarn.lock file
            
        Returns:
            List of InstalledPackage objects
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Lock file not found: {file_path}")
        
        packages: List[InstalledPackage] = []
        seen_packages: set = set()  # Track (name, version) to avoid duplicates
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        logger.debug(f"Parsing {file_path}")
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this is a package entry line
            package_names = self._parse_entry_line(line)
            if package_names:
                # Look for version in subsequent lines
                version = self._find_version(lines, i + 1)
                
                if version:
                    for name in package_names:
                        key = (name, version)
                        if key not in seen_packages:
                            seen_packages.add(key)
                            try:
                                packages.append(InstalledPackage(
                                    name=name,
                                    version=version,
                                    file_path=file_path,
                                    file_type=LockFileType.YARN
                                ))
                            except ValueError as e:
                                logger.warning(f"Skipping invalid package {name}: {e}")
            
            i += 1
        
        logger.debug(f"Extracted {len(packages)} packages from {file_path.name}")
        return packages
    
    def _parse_entry_line(self, line: str) -> List[str]:
        """
        Parse a package entry line and extract package names.
        
        Examples:
            '@babel/core@^7.0.0":' -> ["@babel/core"]
            'lodash@^4.17.0, lodash@^4.17.21:' -> ["lodash"]
            '"react@^17.0.0", "react@^18.0.0":' -> ["react"]
        
        Returns:
            List of unique package names (without version specifiers)
        """
        line = line.rstrip()
        
        # Skip empty lines, comments, and non-entry lines
        if not line or line.startswith("#") or not line.endswith(":"):
            return []
        
        # Remove trailing colon
        line = line[:-1]
        
        # Split by comma to handle multiple specifiers
        # "lodash@^4.17.0", "lodash@^4.17.21"
        specifiers = [s.strip().strip('"').strip("'") for s in line.split(",")]
        
        package_names = set()
        for spec in specifiers:
            name = self._extract_package_name(spec)
            if name:
                package_names.add(name)
        
        return list(package_names)
    
    def _extract_package_name(self, specifier: str) -> Optional[str]:
        """
        Extract package name from a version specifier.
        
        Examples:
            "@babel/core@^7.0.0" -> "@babel/core"
            "lodash@^4.17.0" -> "lodash"
        """
        # Handle scoped packages: @scope/name@version
        if specifier.startswith("@"):
            # Find the second @ which separates name from version
            at_index = specifier.find("@", 1)
            if at_index > 0:
                return specifier[:at_index]
        else:
            # Regular package: name@version
            at_index = specifier.find("@")
            if at_index > 0:
                return specifier[:at_index]
        
        return None
    
    def _find_version(self, lines: List[str], start_index: int) -> Optional[str]:
        """
        Find the version field in the lines following a package entry.
        
        The version line looks like:
            version "1.2.3"
        """
        # Look in the next few lines for the version
        for i in range(start_index, min(start_index + 10, len(lines))):
            line = lines[i]
            
            # Stop if we hit another package entry
            if line and not line[0].isspace() and line.rstrip().endswith(":"):
                break
            
            match = self.VERSION_PATTERN.match(line)
            if match:
                return match.group(1)
        
        return None
