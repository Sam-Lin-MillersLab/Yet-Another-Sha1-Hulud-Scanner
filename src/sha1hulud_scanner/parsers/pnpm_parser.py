"""
Parser for pnpm pnpm-lock.yaml files.
"""

import logging
from pathlib import Path
from typing import List

import yaml

from ..models import InstalledPackage, LockFileType
from .base import BaseLockFileParser

logger = logging.getLogger(__name__)


class PnpmParser(BaseLockFileParser):
    """
    Parser for pnpm pnpm-lock.yaml files.
    
    Uses PyYAML for parsing since pnpm-lock.yaml is valid YAML.
    """
    
    @property
    def file_type(self) -> LockFileType:
        return LockFileType.PNPM
    
    @property
    def filename(self) -> str:
        return "pnpm-lock.yaml"
    
    def parse(self, file_path: Path) -> List[InstalledPackage]:
        """
        Parse a pnpm-lock.yaml file and extract installed packages.
        
        Args:
            file_path: Path to the pnpm-lock.yaml file
            
        Returns:
            List of InstalledPackage objects
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Lock file not found: {file_path}")
        
        packages: List[InstalledPackage] = []
        
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                logger.warning(f"Failed to parse {file_path}: {e}")
                return packages
        
        if not data:
            return packages
        
        logger.debug(f"Parsing {file_path}")
        
        # Handle different pnpm lockfile versions
        # v6+: packages are under "packages" key
        # v5 and earlier: packages are under "packages" key with different format
        packages_obj = data.get("packages", {})
        
        if not packages_obj:
            # Try snapshots for newer pnpm versions
            packages_obj = data.get("snapshots", {})
        
        for key, info in packages_obj.items():
            name, version = self._parse_package_key(key)
            if not name or not version:
                continue
            
            try:
                packages.append(InstalledPackage(
                    name=name,
                    version=version,
                    file_path=file_path,
                    file_type=LockFileType.PNPM
                ))
            except ValueError as e:
                logger.warning(f"Skipping invalid package {name}: {e}")
        
        logger.debug(f"Extracted {len(packages)} packages from {file_path.name}")
        return packages
    
    def _parse_package_key(self, key: str) -> tuple:
        """
        Parse package name and version from pnpm package key.
        
        Formats:
            - "/@scope/name@version" or "/name@version" (v6+)
            - "/@scope/name/version" or "/name/version" (older)
            - "name@version" (some versions)
        
        Returns:
            Tuple of (name, version) or (None, None) if parsing fails
        """
        # Remove leading slash if present
        key = key.lstrip("/")
        
        if not key:
            return (None, None)
        
        # Handle scoped packages: @scope/name@version or @scope/name/version
        if key.startswith("@"):
            # Find the second @ or / that separates name from version
            # Format: @scope/name@version
            parts = key.split("@")
            if len(parts) >= 3:
                # @scope/name@version -> ["", "scope/name", "version"]
                name = f"@{parts[1]}"
                version = parts[2].split("(")[0]  # Remove any peer deps in parens
                return (name, version)
            
            # Try format: @scope/name/version
            parts = key.split("/")
            if len(parts) >= 3:
                name = f"{parts[0]}/{parts[1]}"
                version = parts[2].split("(")[0]
                return (name, version)
        else:
            # Regular package: name@version or name/version
            if "@" in key:
                parts = key.split("@")
                if len(parts) >= 2:
                    name = parts[0]
                    version = parts[1].split("(")[0]
                    return (name, version)
            elif "/" in key:
                parts = key.split("/")
                if len(parts) >= 2:
                    name = parts[0]
                    version = parts[1].split("(")[0]
                    return (name, version)
        
        return (None, None)
