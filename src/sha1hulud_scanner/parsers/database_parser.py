"""
Database parser for loading vulnerable packages from packages.md and wiz-packages.csv.
"""

import csv
import logging
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

from ..models import VulnerablePackage

logger = logging.getLogger(__name__)


class DatabaseParser:
    """
    Parser for the vulnerable packages database files.
    
    Handles both packages.md (markdown list format) and wiz-packages.csv (CSV format).
    """
    
    # Pattern for packages.md entries: "- package@version" or "- @scope/package@version"
    # Split from the last @ to handle scoped packages
    MD_PATTERN = re.compile(r"^-\s+(.+)$")
    
    def __init__(self, db_path: Path) -> None:
        """
        Initialize the database parser.
        
        Args:
            db_path: Path to the directory containing packages.md and wiz-packages.csv
            
        Raises:
            FileNotFoundError: If the database directory doesn't exist
        """
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Error: Vulnerable packages database not found at: {self.db_path}"
            )
        if not self.db_path.is_dir():
            raise ValueError(
                f"Error: Database path must be a directory: {self.db_path}"
            )
    
    def load_all(self) -> Tuple[Set[Tuple[str, str]], Dict[str, List[str]]]:
        """
        Load all vulnerable packages from both database files.
        
        Returns:
            Tuple of:
                - Set of (name, version) tuples for O(1) lookup
                - Dict mapping package names to list of vulnerable versions
                
        Raises:
            FileNotFoundError: If required database files are missing
        """
        packages_md_path = self.db_path / "packages.md"
        wiz_csv_path = self.db_path / "wiz-packages.csv"
        
        # Check for at least one database file
        if not packages_md_path.exists() and not wiz_csv_path.exists():
            raise FileNotFoundError(
                f"Error: No database files found in {self.db_path}. "
                f"Expected packages.md and/or wiz-packages.csv"
            )
        
        vulnerable_set: Set[Tuple[str, str]] = set()
        vulnerable_by_name: Dict[str, List[str]] = {}
        
        # Load packages.md if it exists
        if packages_md_path.exists():
            md_packages = self._parse_packages_md(packages_md_path)
            for pkg in md_packages:
                vulnerable_set.add(pkg.key)
                if pkg.name not in vulnerable_by_name:
                    vulnerable_by_name[pkg.name] = []
                if pkg.version not in vulnerable_by_name[pkg.name]:
                    vulnerable_by_name[pkg.name].append(pkg.version)
            logger.debug(f"Loaded {len(md_packages)} entries from packages.md")
        
        # Load wiz-packages.csv if it exists
        if wiz_csv_path.exists():
            csv_packages = self._parse_wiz_csv(wiz_csv_path)
            for pkg in csv_packages:
                vulnerable_set.add(pkg.key)
                if pkg.name not in vulnerable_by_name:
                    vulnerable_by_name[pkg.name] = []
                if pkg.version not in vulnerable_by_name[pkg.name]:
                    vulnerable_by_name[pkg.name].append(pkg.version)
            logger.debug(f"Loaded {len(csv_packages)} entries from wiz-packages.csv")
        
        logger.debug(f"Total unique vulnerable packages: {len(vulnerable_set)}")
        return vulnerable_set, vulnerable_by_name
    
    def _parse_packages_md(self, file_path: Path) -> List[VulnerablePackage]:
        """
        Parse the packages.md file.
        
        Format: "- package@version" or "- @scope/package@version"
        """
        packages: List[VulnerablePackage] = []
        
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line or not line.startswith("-"):
                    continue
                
                match = self.MD_PATTERN.match(line)
                if not match:
                    logger.warning(
                        f"Skipping malformed entry at line {line_num} in packages.md: {line}"
                    )
                    continue
                
                entry = match.group(1).strip()
                
                # Split from the last @ to handle scoped packages (@scope/name@version)
                last_at = entry.rfind("@")
                if last_at <= 0:  # No @ or @ is first char (scoped package without version)
                    logger.warning(
                        f"Skipping malformed entry at line {line_num} in packages.md: "
                        f"missing version separator: {line}"
                    )
                    continue
                
                name = entry[:last_at]
                version = entry[last_at + 1:]
                
                if not name or not version:
                    logger.warning(
                        f"Skipping malformed entry at line {line_num} in packages.md: "
                        f"empty name or version: {line}"
                    )
                    continue
                
                try:
                    packages.append(VulnerablePackage(
                        name=name,
                        version=version,
                        source="packages.md"
                    ))
                except ValueError as e:
                    logger.warning(
                        f"Skipping invalid entry at line {line_num} in packages.md: {e}"
                    )
        
        return packages
    
    def _parse_wiz_csv(self, file_path: Path) -> List[VulnerablePackage]:
        """
        Parse the wiz-packages.csv file.
        
        Format: Package,Version where Version can have "= X.Y.Z" or "= X.Y.Z || = A.B.C"
        """
        packages: List[VulnerablePackage] = []
        
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
                try:
                    name = row.get("Package", "").strip()
                    version_spec = row.get("Version", "").strip()
                    
                    if not name or not version_spec:
                        logger.warning(
                            f"Skipping malformed entry at row {row_num} in wiz-packages.csv: "
                            f"missing package name or version"
                        )
                        continue
                    
                    # Parse version spec: "= X.Y.Z" or "= X.Y.Z || = A.B.C"
                    versions = self._parse_version_spec(version_spec)
                    
                    for version in versions:
                        try:
                            packages.append(VulnerablePackage(
                                name=name,
                                version=version,
                                source="wiz-packages.csv"
                            ))
                        except ValueError as e:
                            logger.warning(
                                f"Skipping invalid version at row {row_num} in wiz-packages.csv: {e}"
                            )
                
                except Exception as e:
                    logger.warning(
                        f"Skipping malformed entry at row {row_num} in wiz-packages.csv: {e}"
                    )
        
        return packages
    
    def _parse_version_spec(self, spec: str) -> List[str]:
        """
        Parse a version specification string.
        
        Handles formats like:
        - "= 1.0.0"
        - "= 1.0.0 || = 2.0.0"
        
        Returns:
            List of version strings
        """
        versions: List[str] = []
        
        # Split by || for multiple versions
        parts = spec.split("||")
        
        for part in parts:
            part = part.strip()
            # Remove "= " prefix
            if part.startswith("="):
                part = part[1:].strip()
            if part:
                versions.append(part)
        
        return versions
