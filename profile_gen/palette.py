"""Every colour the generated SVGs are allowed to use."""

from __future__ import annotations

DARK = {"bg": "#0d1117", "border": "#3d444d", "text": "#f0f6fc", "muted": "#9198a1"}
LIGHT = {"bg": "#ffffff", "border": "#d1d9e0", "text": "#1f2328", "muted": "#59636e"}

# The terminal window stays dark in both colour schemes.
TERMINAL = {
    "bg": "#0b0d10",
    "bar": "#14171c",
    "line": "#232830",
    "fg": "#d7dbe0",
    "amber": "#e8b45a",
    "dim": "#6b7380",
    "ok": "#7fc8a9",
    "blue": "#8eaae4",
    "white": "#ffffff",
}

STATUS = {"ok": "#3FB950", "fail": "#F85149", "unknown": "#6b7380"}

# WCAG thresholds on the card background.
STROKE_MIN_CONTRAST = 3.0
TEXT_MIN_CONTRAST = 4.5


def norm(color: str) -> str:
    """Lower-case six-digit form of a hex colour."""
    c = color.strip().lower()
    if c.startswith("#") and len(c) == 4:
        c = "#" + "".join(ch * 2 for ch in c[1:])
    return c
