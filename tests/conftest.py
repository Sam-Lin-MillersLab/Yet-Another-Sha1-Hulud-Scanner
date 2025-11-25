"""
Pytest configuration and shared fixtures for sha1hulud_scanner tests.
"""

import pytest
from pathlib import Path


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_packages_md(fixtures_dir: Path) -> Path:
    """Return the path to sample packages.md file."""
    return fixtures_dir / "sample_vulnerable_db" / "packages.md"


@pytest.fixture
def sample_wiz_csv(fixtures_dir: Path) -> Path:
    """Return the path to sample wiz-packages.csv file."""
    return fixtures_dir / "sample_vulnerable_db" / "wiz-packages.csv"


@pytest.fixture
def sample_package_lock(fixtures_dir: Path) -> Path:
    """Return the path to sample package-lock.json file."""
    return fixtures_dir / "package-lock.json"


@pytest.fixture
def sample_yarn_lock(fixtures_dir: Path) -> Path:
    """Return the path to sample yarn.lock file."""
    return fixtures_dir / "yarn.lock"


@pytest.fixture
def sample_pnpm_lock(fixtures_dir: Path) -> Path:
    """Return the path to sample pnpm-lock.yaml file."""
    return fixtures_dir / "pnpm-lock.yaml"


@pytest.fixture
def data_dir() -> Path:
    """Return the path to the real data directory with vulnerability databases."""
    return Path(__file__).parent.parent / "data"
