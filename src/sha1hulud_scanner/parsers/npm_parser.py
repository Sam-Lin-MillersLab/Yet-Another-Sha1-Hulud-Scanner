"""
Parser for npm package-lock.json files.
"""

import json
import logging
from pathlib import Path
from typing import List

from ..models import InstalledPackage, LockFileType
from .base import BaseLockFileParser

logger = logging.getLogger(__name__)


class NpmParser(BaseLockFileParser):
    """
    Parser for npm package-lock.json files.
    
    Supports lockfileVersion 1, 2, and 3.
    """
    
    @property
    def file_type(self) -> LockFileType:
        return LockFileType.NPM
    
    @property
    def filename(self) -> str:
        return "package-lock.json"
    
    def parse(self, file_path: Path) -> List[InstalledPackage]:
        """
        Parse a package-lock.json file and extract installed packages.
        
        Args:
            file_path: Path to the package-lock.json file
            
        Returns:
            List of InstalledPackage objects
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Lock file not found: {file_path}")
        
        packages: List[InstalledPackage] = []
        
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse {file_path}: {e}")
                return packages
        
        lockfile_version = data.get("lockfileVersion", 1)
        logger.debug(f"Parsing {file_path} (npm lockfileVersion: {lockfile_version})")
        
        if lockfile_version >= 2:
            # v2/v3: packages in "packages" object with node_modules/ paths
            packages = self._parse_v2_v3(data, file_path)
        else:
            # v1: packages in nested "dependencies" object
            packages = self._parse_v1(data, file_path)
        
        logger.debug(f"Extracted {len(packages)} packages from {file_path.name}")
        return packages
    
    def _parse_v1(self, data: dict, file_path: Path) -> List[InstalledPackage]:
        """Parse lockfileVersion 1 format with nested dependencies."""
        packages: List[InstalledPackage] = []
        dependencies = data.get("dependencies", {})
        
        self._parse_dependencies_recursive(dependencies, file_path, packages)
        
        return packages
    
    def _parse_dependencies_recursive(
        self,
        dependencies: dict,
        file_path: Path,
        packages: List[InstalledPackage]
    ) -> None:
        """Recursively parse nested dependencies in v1 format."""
        for name, info in dependencies.items():
            if not isinstance(info, dict):
                continue
            
            version = info.get("version")
            if version:
                try:
                    packages.append(InstalledPackage(
                        name=name,
                        version=version,
                        file_path=file_path,
                        file_type=LockFileType.NPM
                    ))
                except ValueError as e:
                    logger.warning(f"Skipping invalid package {name}: {e}")
            
            # Recurse into nested dependencies
            nested = info.get("dependencies", {})
            if nested:
                self._parse_dependencies_recursive(nested, file_path, packages)
    
    def _parse_v2_v3(self, data: dict, file_path: Path) -> List[InstalledPackage]:
        """Parse lockfileVersion 2/3 format with flat packages object."""
        packages: List[InstalledPackage] = []
        packages_obj = data.get("packages", {})
        
        for path, info in packages_obj.items():
            if not isinstance(info, dict):
                continue
            
            # Skip the root package (empty string key)
            if path == "":
                continue
            
            # Extract package name from path
            # Format: "node_modules/package" or "node_modules/@scope/package"
            # or nested: "node_modules/parent/node_modules/child"
            name = self._extract_package_name(path)
            if not name:
                continue
            
            version = info.get("version")
            if not version:
                continue
            
            try:
                packages.append(InstalledPackage(
                    name=name,
                    version=version,
                    file_path=file_path,
                    file_type=LockFileType.NPM
                ))
            except ValueError as e:
                logger.warning(f"Skipping invalid package {name}: {e}")
        
        return packages
    
    def _extract_package_name(self, path: str) -> str:
        """
        Extract package name from node_modules path.
        
        Examples:
            "node_modules/lodash" -> "lodash"
            "node_modules/@babel/core" -> "@babel/core"
            "node_modules/foo/node_modules/bar" -> "bar"
        """
        # Split path and find the last node_modules segment
        parts = path.split("/")
        
        # Find the last "node_modules" index
        last_nm_idx = -1
        for i, part in enumerate(parts):
            if part == "node_modules":
                last_nm_idx = i
        
        if last_nm_idx == -1 or last_nm_idx >= len(parts) - 1:
            return ""
        
        # Get the package name (handles scoped packages)
        remaining = parts[last_nm_idx + 1:]
        
        if remaining[0].startswith("@") and len(remaining) >= 2:
            # Scoped package: @scope/name
            return f"{remaining[0]}/{remaining[1]}"
        else:
            return remaining[0]
