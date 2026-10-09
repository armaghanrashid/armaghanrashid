"""UTC offset formatting for the whoami line."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

MINUS = "−"  # real minus sign, not a hyphen


def utc_offset_label(now: datetime, tzname: str) -> str:
    """'UTC−4' for America/Montreal in summer, 'UTC−5' in winter, 'UTC+5:30' for Asia/Kolkata."""
    offset = now.astimezone(ZoneInfo(tzname)).utcoffset()
    assert offset is not None
    minutes = int(offset.total_seconds() // 60)
    sign = MINUS if minutes < 0 else "+"
    hours, rem = divmod(abs(minutes), 60)
    return f"UTC{sign}{hours}" + (f":{rem:02d}" if rem else "")
