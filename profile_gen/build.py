"""Orchestration: statuses -> SVGs -> README."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import ci
from .cards import card_filename, render_card
from .model import load_profile
from .readme import build_readme
from .terminal import render_terminal


def generate(
    root: Path,
    now: datetime | None = None,
    statuses: dict[str, str] | None = None,
    token: str | None = None,
) -> dict[str, Any]:
    root = Path(root)
    now = now or datetime.now(UTC)
    profile = load_profile(root / "profile.yaml")
    if statuses is None:
        statuses = ci.fetch_all(profile["login"], [p["repo"] for p in profile["projects"]], token)

    assets = root / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "media").mkdir(exist_ok=True)
    written = []
    for scheme in ("dark", "light"):
        path = assets / f"terminal-{scheme}.svg"
        path.write_text(render_terminal(profile, statuses, now, scheme), encoding="utf-8")
        written.append(path)
        for project in profile["projects"]:
            path = assets / card_filename(project["repo"], scheme)
            path.write_text(render_card(project, scheme), encoding="utf-8")
            written.append(path)
    readme = root / "README.md"
    readme.write_text(build_readme(profile, statuses, now, root), encoding="utf-8")
    written.append(readme)
    return {"profile": profile, "statuses": statuses, "files": written}
