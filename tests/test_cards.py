from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from profile_gen.cards import (
    CONTENT_W,
    DESC_LINES,
    DESC_SIZE,
    HEIGHT,
    WIDTH,
    card_colors,
    layout,
    render_card,
)
from profile_gen.colors import contrast, darken_to_contrast, light_variants
from profile_gen.diagrams import DIAGRAMS
from profile_gen.palette import DARK, LIGHT
from profile_gen.wrap import MONO_EM, SANS_EM, text_width, wrap

SVG = "{http://www.w3.org/2000/svg}"


def test_contrast_reference_values():
    assert contrast("#000000", "#ffffff") == pytest.approx(21.0)
    assert contrast("#ffffff", "#ffffff") == pytest.approx(1.0)


def test_light_variants_meet_wcag(profile):
    for p in profile["projects"]:
        stroke, tag = light_variants(p["color"])
        assert contrast(stroke, LIGHT["bg"]) >= 3.0, p["repo"]
        assert contrast(tag, LIGHT["bg"]) >= 4.5, p["repo"]


def test_yellow_is_darkened_but_a_dark_colour_is_kept():
    stroke, tag = light_variants("#CFE23C")
    assert stroke != "#CFE23C" and tag != "#CFE23C"
    assert darken_to_contrast("#1F2328", "#ffffff", 4.5) == "#1F2328"


def test_dark_tag_text_is_readable(profile):
    for p in profile["projects"]:
        assert contrast(p["color"], DARK["bg"]) >= 4.5, p["repo"]


def test_card_uses_project_colour_on_bar_tag_and_strokes(profile):
    for p in profile["projects"]:
        s = render_card(p, "dark")
        assert s.count(p["color"].upper()) >= 3  # bar, tag, strokes/dots
        assert f"fill:{p['color'].upper()}" in s


def test_every_diagram_key_is_covered(profile):
    assert {p["diagram"] for p in profile["projects"]} == set(DIAGRAMS)


def test_cards_parse_and_have_fixed_size(profile):
    for p in profile["projects"]:
        for scheme in ("dark", "light"):
            root = ET.fromstring(render_card(p, scheme))
            assert (root.get("width"), root.get("height")) == (str(WIDTH), str(HEIGHT))


def test_wrap_never_exceeds_width_mono():
    text = "Resume critique that can roast you, with spoken feedback. Built as a team in 24 hours."
    for width in (150, 240, 300, 406):
        for line in wrap(text, width, 12, MONO_EM):
            assert text_width(line, 12, MONO_EM) <= width


def test_wrap_rejects_overflow_instead_of_truncating():
    with pytest.raises(ValueError):
        wrap("a b c d e f g h i j " * 10, 100, 12, MONO_EM, max_lines=2)
    with pytest.raises(ValueError):
        wrap("supercalifragilisticexpialidocious", 50, 12, MONO_EM)


def test_wrap_preserves_every_word():
    text = "one two three four five six seven eight nine ten"
    assert " ".join(wrap(text, 80, 12, MONO_EM)) == text


def test_card_text_fits_inside_card(profile):
    for p in profile["projects"]:
        lay = layout(p)
        assert len(lay["desc_lines"]) <= DESC_LINES
        for line in lay["desc_lines"]:
            assert text_width(line, DESC_SIZE, SANS_EM) <= CONTENT_W
        assert lay["name_w"] + lay["tag_w"] < CONTENT_W
        assert lay["stack_w"] <= CONTENT_W
        assert " ".join(lay["desc_lines"]) == p["desc"]


def test_card_colors_light_scheme_uses_neutrals():
    c = card_colors("#CFE23C", "light")
    assert c["bg"] == "#ffffff" and c["text"] == "#1f2328" and c["muted"] == "#59636e"


def test_wrecker_boxes_are_equal_and_unlabelled_by_my_part():
    d = DIAGRAMS["wrecker"]
    assert "my part" not in d
    assert "stroke-width" not in d


def test_quorum_leader_label_fits_its_circle():
    import re

    d = DIAGRAMS["quorum"]
    r = float(re.search(r'<circle cx="40" cy="35" r="([\d.]+)"', d).group(1))
    label = re.search(r">(lead\w*)</text>", d).group(1)
    half_width = len(label) * 9.5 * MONO_EM / 2
    assert r >= half_width + 4
    assert 'x="40" y="38" text-anchor="middle"' in d
