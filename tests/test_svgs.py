from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import UTC, datetime

from profile_gen.cards import card_palette
from profile_gen.palette import DARK, LIGHT, STATUS, TERMINAL, norm

SVG = "{http://www.w3.org/2000/svg}"
NOW_FOR_TESTS = datetime(2026, 10, 9, 7, 12, tzinfo=UTC)


def palette(profile) -> set[str]:
    allowed = {norm(c) for c in [*DARK.values(), *LIGHT.values(), *TERMINAL.values()]}
    allowed |= {norm(c) for c in STATUS.values()}
    for p in profile["projects"]:
        allowed |= card_palette(p)
    return allowed


def texts(svg_path):
    root = ET.parse(svg_path).getroot()
    return ["".join(t.itertext()) for t in root.iter(f"{SVG}text")]


def test_every_svg_parses(built):
    files = sorted((built / "assets").glob("*.svg"))
    assert len(files) == 2 + 12
    for f in files:
        assert ET.parse(f).getroot().tag == f"{SVG}svg", f.name


def test_only_palette_colours(built, profile):
    allowed = palette(profile)
    for f in (built / "assets").glob("*.svg"):
        found = {norm(c) for c in re.findall(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b", f.read_text())}
        assert found <= allowed, (f.name, found - allowed)
        assert not re.search(r"rgb\(|hsl\(|gradient", f.read_text(), re.I), f.name


def test_no_gradients_glow_or_external_resources(built):
    for f in (built / "assets").glob("*.svg"):
        s = f.read_text()
        assert not re.search(r"<(linear|radial)Gradient|<filter|@import|drop-shadow", s)
        assert "http://" not in s.replace("http://www.w3.org/2000/svg", "")
        assert "https://" not in s


def test_terminal_content(built, profile):
    lines = texts(built / "assets" / "terminal-dark.svg")
    assert "based in Montreal, Canada · tz America/Montreal (UTC−4)" in lines
    assert "[ok] software engineering · data engineering · AI/ML · 2027 · Montreal / remote" in lines
    assert not any("last checked" in line for line in lines)
    for cmd in ("whoami", "tail -n 4 experience.log", "ls builds/", "./open-to --roles"):
        assert any(line.endswith(cmd) for line in lines), cmd


def test_terminal_ci_symbols_follow_statuses(built, profile, statuses):
    s = (built / "assets" / "terminal-dark.svg").read_text()
    assert s.count("✔") == list(statuses.values()).count("ok")
    assert s.count("✘") == list(statuses.values()).count("fail")


def test_ls_names_use_project_colours(built, profile):
    s = (built / "assets" / "terminal-dark.svg").read_text()
    for p in profile["projects"]:
        assert f'<tspan fill="{p["color"].upper()}">{p["repo"]}/</tspan>' in s


def test_terminal_variants_differ_only_in_frame(built):
    dark = (built / "assets" / "terminal-dark.svg").read_text()
    light = (built / "assets" / "terminal-light.svg").read_text()
    assert dark != light
    assert dark.replace(DARK["border"], LIGHT["border"]) == light


def test_terminal_animation_contract(built):
    s = (built / "assets" / "terminal-light.svg").read_text()
    assert "prefers-reduced-motion:reduce" in s
    assert "both" in s  # fill-mode keeps the final state
    assert "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace" in s
    assert "blink" in s or "@keyframes bl" in s
    delays = [float(d) for d in re.findall(r"animation-delay:([\d.]+)s", s)]
    assert 3.5 <= max(delays) <= 4.6


def test_terminal_text_is_xml_escaped(tmp_path, profile, statuses):
    from datetime import datetime

    from profile_gen.terminal import render_terminal

    p = {**profile, "name": 'A&B <x> "q"'}
    svg = render_terminal(p, statuses, datetime(2026, 1, 1, tzinfo=UTC), "dark")
    root = ET.fromstring(svg)
    assert any("A&B <x>" in "".join(t.itertext()) for t in root.iter(f"{SVG}text"))


def test_no_static_zero_opacity_so_non_animating_renderers_show_everything(built):
    for f in (built / "assets").glob("*.svg"):
        s = f.read_text()
        css = re.sub(r"@keyframes\s+\w+\s*\{(?:[^{}]|\{[^{}]*\})*\}", "", s)  # drop keyframes
        assert not re.search(r"opacity\s*:\s*0(?![.\d])", css), f.name
        for el in ET.parse(f).getroot().iter():
            assert el.get("opacity") not in ("0", "0.0"), (f.name, el.tag)
            assert el.get("fill-opacity") not in ("0", "0.0"), (f.name, el.tag)


def test_animations_start_hidden_only_through_fill_mode(built):
    s = (built / "assets" / "terminal-dark.svg").read_text()
    assert "@keyframes fi{from{opacity:0}to{opacity:1}}" in s
    assert ".a{animation:fi .12s linear both}" in s


def test_terminal_height_fits_content_exactly(built, profile, statuses):
    from profile_gen.terminal import BAR_H, LH, PAD_B, PAD_T, build_lines

    n = len(build_lines(profile, statuses, NOW_FOR_TESTS))
    root = ET.parse(built / "assets" / "terminal-dark.svg").getroot()
    height = int(root.get("height"))
    assert height == BAR_H + PAD_T + LH * n + PAD_B
    window = next(r for r in root.iter(f"{SVG}rect") if r.get("rx") == "8" and r.get("y") == "0.5")
    assert float(window.get("y")) + float(window.get("height")) + 0.5 == height
    last_baseline = max(float(t.get("y")) for t in root.iter(f"{SVG}text"))
    assert height - last_baseline < 30


def test_typing_covers_are_collapsed_without_css(built):
    """If the stylesheet is ignored entirely, the cover rects must not hide any text."""
    root = ET.parse(built / "assets" / "terminal-dark.svg").getroot()
    covers = [r for r in root.iter(f"{SVG}rect") if r.get("class") == "t"]
    assert len(covers) == 5
    assert all(r.get("transform") == "scale(0)" for r in covers)
