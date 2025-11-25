"""
Core scanner logic for detecting vulnerable packages.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .models import (
    InstalledPackage,
    LockFileType,
    ScanResult,
    ScanSummary,
)
from .parsers import (
    BaseLockFileParser,
    DatabaseParser,
    NpmParser,
    YarnParser,
    PnpmParser,
)

logger = logging.getLogger(__name__)


class Scanner:
    """
    Core scanner for detecting vulnerable packages in lock files.
    """
    
    # Supported lock file names
    LOCK_FILE_NAMES = {
        "package-lock.json": LockFileType.NPM,
        "yarn.lock": LockFileType.YARN,
        "pnpm-lock.yaml": LockFileType.PNPM,
    }
    
    def __init__(self, db_path: Path) -> None:
        """
        Initialize the scanner.
        
        Args:
            db_path: Path to the directory containing vulnerability database files
            
        Raises:
            FileNotFoundError: If database directory doesn't exist
        """
        self.db_path = Path(db_path)
        self._db_parser = DatabaseParser(self.db_path)
        
        # Load vulnerability database
        self._vulnerable_set: Set[Tuple[str, str]] = set()
        self._vulnerable_by_name: Dict[str, List[str]] = {}
        self._load_database()
        
        # Initialize parsers
        self._parsers: List[BaseLockFileParser] = [
            NpmParser(),
            YarnParser(),
            PnpmParser(),
        ]
    
    def _load_database(self) -> None:
        """Load the vulnerability database."""
        self._vulnerable_set, self._vulnerable_by_name = self._db_parser.load_all()
        logger.debug(f"Loaded {len(self._vulnerable_set)} vulnerable package entries")
    
    def scan_file(self, file_path: Path) -> ScanSummary:
        """
        Scan a single lock file for vulnerable packages.
        
        Args:
            file_path: Path to the lock file to scan
            
        Returns:
            ScanSummary with results
        """
        file_path = Path(file_path).resolve()
        
        summary = ScanSummary(
            scan_date=datetime.now(timezone.utc),
            target_path=file_path,
        )
        
        if not file_path.exists():
            summary.add_warning(f"File not found: {file_path}")
            return summary
        
        if not file_path.is_file():
            summary.add_warning(f"Path is not a file: {file_path}")
            return summary
        
        # Find appropriate parser
        parser = self._get_parser_for_file(file_path)
        if not parser:
            summary.add_warning(f"No parser available for: {file_path.name}")
            return summary
        
        # Parse the lock file
        try:
            packages = parser.parse(file_path)
            summary.increment_files_scanned()
            logger.debug(f"Parsed {len(packages)} packages from {file_path}")
        except Exception as e:
            summary.add_warning(f"Failed to parse {file_path}: {e}")
            return summary
        
        # Match against vulnerability database
        results = self.match_packages(packages)
        for result in results:
            summary.add_result(result)
        
        return summary
    
    def scan_directory(self, dir_path: Path) -> ScanSummary:
        """
        Recursively scan a directory for lock files and check for vulnerable packages.
        
        Args:
            dir_path: Path to the directory to scan
            
        Returns:
            ScanSummary with aggregated results
        """
        dir_path = Path(dir_path).resolve()
        
        summary = ScanSummary(
            scan_date=datetime.now(timezone.utc),
            target_path=dir_path,
        )
        
        if not dir_path.exists():
            summary.add_warning(f"Directory not found: {dir_path}")
            return summary
        
        if not dir_path.is_dir():
            summary.add_warning(f"Path is not a directory: {dir_path}")
            return summary
        
        # Discover all lock files
        lock_files = self.discover_lock_files(dir_path)
        
        if not lock_files:
            logger.debug(f"No lock files found in: {dir_path}")
            return summary
        
        logger.debug(f"Found {len(lock_files)} lock files in {dir_path}")
        
        # Scan each lock file
        for lock_file in lock_files:
            file_summary = self.scan_file(lock_file)
            
            # Merge results
            summary.files_scanned += file_summary.files_scanned
            for result in file_summary.vulnerabilities:
                summary.add_result(result)
            for warning in file_summary.warnings:
                summary.add_warning(warning)
        
        return summary
    
    def scan(self, path: Path) -> ScanSummary:
        """
        Scan a file or directory for vulnerable packages.
        
        Automatically detects whether the path is a file or directory.
        
        Args:
            path: Path to scan (file or directory)
            
        Returns:
            ScanSummary with results
        """
        path = Path(path).resolve()
        
        if path.is_file():
            return self.scan_file(path)
        elif path.is_dir():
            return self.scan_directory(path)
        else:
            summary = ScanSummary(
                scan_date=datetime.now(timezone.utc),
                target_path=path,
            )
            summary.add_warning(f"Path not found: {path}")
            return summary
    
    def match_packages(self, packages: List[InstalledPackage]) -> List[ScanResult]:
        """
        Match a list of installed packages against the vulnerability database.
        
        Args:
            packages: List of installed packages to check
            
        Returns:
            List of ScanResult for packages that match vulnerabilities
        """
        results: List[ScanResult] = []
        
        for pkg in packages:
            # O(1) lookup using set
            if pkg.key in self._vulnerable_set:
                # Get all vulnerable versions for this package
                vulnerable_versions = self._vulnerable_by_name.get(pkg.name, [pkg.version])
                
                result = ScanResult(
                    package_name=pkg.name,
                    installed_version=pkg.version,
                    vulnerable_versions=vulnerable_versions,
                    file_path=pkg.file_path,
                    file_type=pkg.file_type,
                )
                results.append(result)
                logger.debug(f"Found match: {pkg.name}@{pkg.version}")
        
        return results
    
    def discover_lock_files(self, dir_path: Path) -> List[Path]:
        """
        Recursively discover all lock files in a directory.
        
        Args:
            dir_path: Directory to search
            
        Returns:
            List of paths to lock files found
        """
        lock_files: List[Path] = []
        
        try:
            for item in dir_path.rglob("*"):
                if item.is_file() and item.name in self.LOCK_FILE_NAMES:
                    # Skip node_modules to avoid scanning dependency lock files
                    if "node_modules" not in item.parts:
                        lock_files.append(item)
                        logger.debug(f"Found: {item}")
        except PermissionError as e:
            logger.warning(f"Permission denied accessing: {e}")
        
        return lock_files
    
    def _get_parser_for_file(self, file_path: Path) -> Optional[BaseLockFileParser]:
        """Get the appropriate parser for a lock file."""
        for parser in self._parsers:
            if parser.can_parse(file_path):
                return parser
        return None
    
    def register_parser(self, parser: BaseLockFileParser) -> None:
        """
        Register an additional parser.
        
        Args:
            parser: Parser instance to register
        """
        self._parsers.append(parser)
        # Update supported lock file names
        self.LOCK_FILE_NAMES[parser.filename] = parser.file_type
