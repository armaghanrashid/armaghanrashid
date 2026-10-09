from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

import pytest

from profile_gen import ci
from profile_gen.build import generate
from profile_gen.model import load_profile

ROOT = Path(__file__).resolve().parent.parent
NOW = datetime(2026, 10, 9, 7, 12, tzinfo=UTC)  # DST in Montreal: UTC-4


@pytest.fixture(scope="session")
def profile():
    return load_profile(ROOT / "profile.yaml")


@pytest.fixture
def statuses(profile):
    cycle = [ci.OK, ci.FAIL, ci.UNKNOWN]
    return {p["repo"]: cycle[i % 3] for i, p in enumerate(profile["projects"])}


@pytest.fixture
def built(tmp_path, statuses):
    """A full generation into a scratch copy of the repo (no media files)."""
    shutil.copy(ROOT / "profile.yaml", tmp_path / "profile.yaml")
    generate(tmp_path, now=NOW, statuses=statuses)
    return tmp_path
