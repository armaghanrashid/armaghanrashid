"""Text measurement and wrapping with a conservative per-character width model."""

from __future__ import annotations

MONO_EM = 0.6  # width of one monospace character, in em
SANS_EM = 0.53  # upper bound for the proportional UI font stack (Segoe UI, SF, Helvetica ~0.50)


def text_width(text: str, size: float, em: float = MONO_EM, letter_spacing: float = 0.0) -> float:
    return len(text) * (size * em + letter_spacing)


def wrap(text: str, max_width: float, size: float, em: float = MONO_EM, max_lines: int | None = None):
    """Greedy word wrap. Raises ValueError rather than overflow or silently drop words."""
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        if text_width(word, size, em) > max_width:
            raise ValueError(f"word {word!r} is wider than {max_width}px")
        trial = word if not cur else f"{cur} {word}"
        if text_width(trial, size, em) <= max_width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if max_lines is not None and len(lines) > max_lines:
        raise ValueError(f"needs {len(lines)} lines, limit is {max_lines}: {text!r}")
    return lines
