"""Featured-build cards: one standalone SVG per project and colour scheme."""

from __future__ import annotations

from typing import Any

from .colors import light_variants
from .diagrams import DIAGRAMS
from .palette import DARK, LIGHT, norm
from .svgutil import MONO, SANS, attr, esc, num
from .wrap import MONO_EM, SANS_EM, text_width, wrap

WIDTH, HEIGHT = 440, 190
BAR = 3
PAD_L, PAD_R = 18, 14
CONTENT_W = WIDTH - PAD_L - PAD_R

NAME_SIZE, TAG_SIZE, TAG_SPACING = 15, 10, 0.6
DESC_SIZE, DESC_LH, DESC_LINES = 11.5, 16, 2
STACK_SIZE = 11
DIAGRAM_SCALE = 1.1
DIAGRAM_W, DIAGRAM_H = 300 * DIAGRAM_SCALE, 70 * DIAGRAM_SCALE

NAME_Y, DESC_Y, DIAGRAM_Y, STACK_Y = 30, 53, 80, 178


def card_colors(color: str, scheme: str) -> dict[str, str]:
    """Neutrals plus the accent colours (stroke, text) for the given scheme."""
    if scheme == "dark":
        return {**DARK, "stroke": color.upper(), "tag": color.upper()}
    stroke, tag = light_variants(color, LIGHT["bg"])
    return {**LIGHT, "stroke": stroke, "tag": tag}


def layout(project: dict[str, Any]) -> dict[str, Any]:
    """Wrapped text and every measured width, so tests can check nothing overflows."""
    tag = project["tag"].upper()
    stack = " · ".join(project["stack"])
    desc_lines = wrap(project["desc"], CONTENT_W, DESC_SIZE, SANS_EM, DESC_LINES)
    return {
        "name_w": text_width(project["repo"], NAME_SIZE, MONO_EM),
        "tag": tag,
        "tag_w": text_width(tag, TAG_SIZE, MONO_EM, TAG_SPACING),
        "desc_lines": desc_lines,
        "stack": stack,
        "stack_w": text_width(stack, STACK_SIZE, MONO_EM),
    }


def render_card(project: dict[str, Any], scheme: str) -> str:
    c = card_colors(project["color"], scheme)
    lay = layout(project)
    if lay["name_w"] + lay["tag_w"] + 16 > CONTENT_W:
        raise ValueError(f"{project['repo']}: name and tag do not fit on one row")
    if lay["stack_w"] > CONTENT_W:
        raise ValueError(f"{project['repo']}: stack line is too wide")

    dx = PAD_L + (CONTENT_W - DIAGRAM_W) / 2
    desc = "".join(
        f'<text x="{PAD_L}" y="{DESC_Y + i * DESC_LH}" class="d">{esc(line)}</text>'
        for i, line in enumerate(lay["desc_lines"])
    )
    summary = f"{project['repo']}: {project['desc']}"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label={attr(summary)}>
<title>{esc(summary)}</title>
<style>
text{{font-family:{MONO}}}
.n{{font-size:{NAME_SIZE}px;font-weight:600;fill:{c["text"]}}}
.t{{font-size:{TAG_SIZE}px;letter-spacing:{TAG_SPACING}px;fill:{c["tag"]}}}
.d{{font-family:{SANS};font-size:{DESC_SIZE}px;fill:{c["muted"]}}}
.k{{font-size:{STACK_SIZE}px;fill:{c["muted"]}}}
.s{{stroke:{c["stroke"]};fill:none;stroke-width:1.4}}
.f{{fill:{c["stroke"]}}}
.m{{fill:{c["muted"]};font-size:9.5px}}
.g{{stroke:{c["border"]};stroke-width:1;fill:none}}
</style>
<defs><clipPath id="r"><rect width="{WIDTH}" height="{HEIGHT}" rx="6"/></clipPath></defs>
<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="6" fill="{c["bg"]}" stroke="{c["border"]}"/>
<rect width="{BAR}" height="{HEIGHT}" fill="{c["stroke"]}" clip-path="url(#r)"/>
<text x="{PAD_L}" y="{NAME_Y}" class="n">{esc(project["repo"])}</text>
<text x="{WIDTH - PAD_R}" y="{NAME_Y}" text-anchor="end" class="t">{esc(lay["tag"])}</text>
{desc}
<g transform="translate({num(dx)} {DIAGRAM_Y}) scale({DIAGRAM_SCALE})">{DIAGRAMS[project["diagram"]]}</g>
<text x="{PAD_L}" y="{STACK_Y}" class="k">{esc(lay["stack"])}</text>
</svg>
"""


def card_filename(repo: str, scheme: str) -> str:
    return f"card-{repo}-{scheme}.svg"


def card_palette(project: dict[str, Any]) -> set[str]:
    out = {norm(project["color"])}
    for scheme in ("dark", "light"):
        c = card_colors(project["color"], scheme)
        out |= {norm(c["stroke"]), norm(c["tag"])}
    return out
