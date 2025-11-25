"""
Command-line interface for the Shai-Hulud 2.0 Scanner.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from . import __version__
from .models import OutputFormat
from .output import ConsoleOutput
from .scanner import Scanner

# Exit codes
EXIT_SUCCESS = 0
EXIT_VULNERABILITIES = 1
EXIT_ERROR = 2

# Default database path (relative to package or repo root)
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data"


def setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.WARNING
    
    # Configure handler for stderr
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    
    # Use a simple format for debug output
    if verbose:
        formatter = logging.Formatter("[%(levelname)s] %(message)s")
    else:
        formatter = logging.Formatter("%(message)s")
    
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="sha1hulud-scanner",
        description="Scan package lock files for packages affected by the Shai-Hulud 2.0 supply chain attack",
        epilog="Exit codes: 0 = no vulnerabilities, 1 = vulnerabilities found, 2 = error",
    )
    
    parser.add_argument(
        "path",
        type=str,
        help="File or directory path to scan",
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output file path (writes results to file)",
    )
    
    parser.add_argument(
        "-f", "--format",
        type=str,
        choices=["console", "json"],
        default="console",
        help="Output format: console (default) or json",
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose/debug logging",
    )
    
    parser.add_argument(
        "-d", "--db-path",
        type=str,
        default=None,
        help="Custom path to vulnerable packages database directory",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    
    return parser


def get_db_path(custom_path: Optional[str] = None) -> Path:
    """
    Determine the database path to use.
    
    Args:
        custom_path: User-specified custom database path
        
    Returns:
        Path to the database directory
    """
    if custom_path:
        return Path(custom_path)
    
    # Try default path relative to package
    if DEFAULT_DB_PATH.exists():
        return DEFAULT_DB_PATH
    
    # Try current directory
    cwd_data = Path.cwd() / "data"
    if cwd_data.exists():
        return cwd_data
    
    return DEFAULT_DB_PATH


def main(args: Optional[list] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command-line arguments (defaults to sys.argv)
        
    Returns:
        Exit code
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # Setup logging
    setup_logging(parsed_args.verbose)
    logger = logging.getLogger(__name__)
    
    # Validate path
    target_path = Path(parsed_args.path)
    if not target_path.exists():
        print(f"Error: Path not found: {target_path}", file=sys.stderr)
        return EXIT_ERROR
    
    # Get database path
    db_path = get_db_path(parsed_args.db_path)
    logger.debug(f"Using database path: {db_path}")
    
    # Initialize scanner
    try:
        scanner = Scanner(db_path)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return EXIT_ERROR
    except Exception as e:
        print(f"Error initializing scanner: {e}", file=sys.stderr)
        return EXIT_ERROR
    
    # Run scan
    try:
        summary = scanner.scan(target_path)
    except Exception as e:
        print(f"Error during scan: {e}", file=sys.stderr)
        return EXIT_ERROR
    
    # Handle output
    output_format = OutputFormat(parsed_args.format)
    
    if output_format == OutputFormat.CONSOLE:
        formatter = ConsoleOutput()
        formatter.format(summary)
    elif output_format == OutputFormat.JSON:
        # JSON output will be implemented in Phase 6
        from .output.json_output import JsonOutput
        formatter = JsonOutput()
        output = formatter.format(summary)
        
        if parsed_args.output:
            try:
                with open(parsed_args.output, "w", encoding="utf-8") as f:
                    f.write(output)
                logger.debug(f"Results written to: {parsed_args.output}")
            except IOError as e:
                print(f"Error writing to output file: {e}", file=sys.stderr)
                return EXIT_ERROR
        else:
            print(output)
    
    # Write to file if specified (for console format)
    if parsed_args.output and output_format == OutputFormat.CONSOLE:
        try:
            with open(parsed_args.output, "w", encoding="utf-8") as f:
                console_formatter = ConsoleOutput(stream=f)
                console_formatter.format(summary)
            logger.debug(f"Results written to: {parsed_args.output}")
        except IOError as e:
            print(f"Error writing to output file: {e}", file=sys.stderr)
            return EXIT_ERROR
    
    # Return appropriate exit code
    if summary.has_vulnerabilities:
        return EXIT_VULNERABILITIES
    
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
