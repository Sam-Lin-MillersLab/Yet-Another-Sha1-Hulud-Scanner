"""
JSON output formatter for machine-readable scan results.
"""

import json
from datetime import datetime
from typing import Any, Dict

from ..models import ScanSummary


class JsonOutput:
    """
    Formatter for JSON output.
    """
    
    def format(self, summary: ScanSummary) -> str:
        """
        Format scan results as JSON.
        
        Args:
            summary: Scan summary to format
            
        Returns:
            JSON string
        """
        data = self._to_dict(summary)
        return json.dumps(data, indent=2, default=str)
    
    def _to_dict(self, summary: ScanSummary) -> Dict[str, Any]:
        """Convert ScanSummary to dictionary for JSON serialization."""
        return {
            "scan_date": summary.scan_date.isoformat() if isinstance(summary.scan_date, datetime) else str(summary.scan_date),
            "target_path": str(summary.target_path),
            "files_scanned": summary.files_scanned,
            "vulnerabilities_found": summary.vulnerabilities_found,
            "results": [
                {
                    "package": result.package_name,
                    "version": result.installed_version,
                    "file_type": result.file_type.value,
                    "file_path": str(result.file_path),
                }
                for result in summary.vulnerabilities
            ],
            "warnings": summary.warnings,
        }
