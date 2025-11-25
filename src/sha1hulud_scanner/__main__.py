"""
Entry point for running the scanner as a module.

Usage:
    python -m sha1hulud_scanner [OPTIONS] <PATH>
"""

from .cli import main

if __name__ == "__main__":
    main()
