"""WCAG contrast maths and the light-theme variants of project colours."""

from __future__ import annotations

import colorsys

from .palette import STROKE_MIN_CONTRAST, TEXT_MIN_CONTRAST, norm


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    c = norm(color)
    return int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)


def rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    r, g, b = (max(0, min(255, round(v))) for v in rgb)
    return f"#{r:02X}{g:02X}{b:02X}"


def luminance(color: str) -> float:
    def lin(v: int) -> float:
        s = v / 255
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(v) for v in hex_to_rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def darken_to_contrast(color: str, background: str, minimum: float) -> str:
    """Keep the hue and saturation, lower the lightness until `minimum` is met.

    Returns the colour unchanged (upper-cased) if it already passes.
    """
    if contrast(color, background) >= minimum:
        return rgb_to_hex(hex_to_rgb(color))
    r, g, b = (v / 255 for v in hex_to_rgb(color))
    h, lightness, s = colorsys.rgb_to_hls(r, g, b)
    while lightness > 0:
        lightness = max(0.0, lightness - 0.005)
        cand = rgb_to_hex(tuple(v * 255 for v in colorsys.hls_to_rgb(h, lightness, s)))
        if contrast(cand, background) >= minimum:
            return cand
    return "#000000"


def light_variants(color: str, background: str = "#ffffff") -> tuple[str, str]:
    """(stroke colour at >= 3:1, text colour at >= 4.5:1) on the light card background."""
    return (
        darken_to_contrast(color, background, STROKE_MIN_CONTRAST),
        darken_to_contrast(color, background, TEXT_MIN_CONTRAST),
    )
