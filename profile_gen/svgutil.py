from __future__ import annotations

from xml.sax.saxutils import escape, quoteattr

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"


def esc(text: str) -> str:
    """Escape text for an XML text node."""
    return escape(text)


def attr(text: str) -> str:
    """Escape and quote a value for an XML attribute."""
    return quoteattr(text)


def num(value: float) -> str:
    """Compact number formatting for coordinates."""
    s = f"{value:.2f}".rstrip("0").rstrip(".")
    return s or "0"
