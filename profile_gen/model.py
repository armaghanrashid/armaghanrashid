"""Loading and validating profile.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .diagrams import DIAGRAMS as _DRAWINGS

REQUIRED = [
    "login", "name", "tagline", "education", "location", "timezone", "linkedin", "open_to",
    "summary", "experience", "stack", "projects", "media", "closed_source",
]
PROJECT_KEYS = ["repo", "tag", "color", "desc", "stack", "diagram"]
DIAGRAMS = set(_DRAWINGS)  # every key that has a drawing in diagrams.py


def load_profile(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    missing = [k for k in REQUIRED if k not in data]
    if missing:
        raise ValueError(f"profile.yaml is missing: {', '.join(missing)}")
    for project in data["projects"]:
        absent = [k for k in PROJECT_KEYS if k not in project]
        if absent:
            raise ValueError(f"project {project.get('repo')} is missing: {', '.join(absent)}")
        if project["diagram"] not in DIAGRAMS:
            raise ValueError(f"unknown diagram {project['diagram']!r}")
    data["summary"] = " ".join(str(data["summary"]).split())
    return data
