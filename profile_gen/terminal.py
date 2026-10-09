"""The animated terminal SVG (dark and light framing; the window itself is always dark)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from . import ci
from .palette import DARK, LIGHT, STATUS, TERMINAL, norm
from .svgutil import MONO, attr, esc, num
from .tz import utc_offset_label

WIDTH = 900
FONT = 14
CW = FONT * 0.6  # one monospace cell
LH = 23
BAR_H = 34
PAD_X, PAD_T, PAD_B = 22, 14, 16
SHELL_USER = "armaghan"
COL_PITCH = 27  # three-column grids (ls, ci)

# Run kinds -> CSS class.
PR, PA, CMD, DIM, HEAD, AMB, PLAIN = "pr", "pa", "c", "d", "h", "am", ""
SYMBOL = {ci.OK: ("✔", "ok"), ci.FAIL: ("✘", "bad"), ci.UNKNOWN: ("·", "d")}

Run = tuple[str, str]  # (css class, text)


@dataclass
class Line:
    cells: list[tuple[int, list[Run]]] = field(default_factory=list)  # (column, runs)
    kind: str = "out"  # prompt | out | blank | cursor
    command: str = ""  # for prompt lines: the typed command (also present in cells)
    delay: float = 0.0
    type_dur: float = 0.0
    type_col: int = 0

    def text(self) -> str:
        return " ".join("".join(t for _, t in runs) for _, runs in self.cells)


def prompt_runs(host: str) -> list[Run]:
    return [(PR, f"{SHELL_USER}@{host}"), (PLAIN, ":"), (PA, "~"), (PLAIN, "$ ")]


def build_lines(profile: dict[str, Any], statuses: dict[str, str], now: datetime) -> list[Line]:
    host = profile["location"].split(",")[0].strip().lower()
    prompt = prompt_runs(host)
    plen = sum(len(t) for _, t in prompt)
    lines: list[Line] = []
    clock = [0.2]

    def gap(seconds: float) -> None:
        clock[0] += seconds

    def command(cmd: str, comment: str = "") -> None:
        dur = max(0.12, len(cmd) * 0.028)
        runs: list[Run] = [(CMD, cmd)]
        if comment:
            runs.append((DIM, "   " + comment))
        line = Line(
            cells=[(0, prompt), (plen, runs)], kind="prompt", command=cmd,
            delay=clock[0], type_dur=dur + (len(comment) * 0.004 if comment else 0), type_col=plen,
        )
        lines.append(line)
        gap(0.12 + line.type_dur)

    def out(cells: list[tuple[int, list[Run]]], step: float = 0.07) -> None:
        lines.append(Line(cells=cells, kind="out", delay=clock[0]))
        gap(step)

    def blank() -> None:
        lines.append(Line(kind="blank", delay=clock[0]))
        gap(0.1)

    # whoami
    command("whoami")
    tag = profile["tagline"]
    out([(0, [(HEAD, profile["name"]), (PLAIN, "  "), (DIM, f"// {tag}")])])
    edu = profile["education"].split(" · ")
    edu_runs: list[Run] = []
    for i, part in enumerate(edu):
        if i:
            edu_runs += [(PLAIN, " "), (DIM, "·"), (PLAIN, " ")]
        edu_runs.append((PLAIN, part))
    out([(0, edu_runs)])
    offset = utc_offset_label(now, profile["timezone"])
    out([(0, [
        (PLAIN, f"based in {profile['location']} "), (DIM, "·"),
        (PLAIN, f" tz {profile['timezone']} ({offset})"),
    ])])
    blank()

    # experience
    exp = profile["experience"]
    command(f"tail -n {len(exp)} experience.log")
    c_org = 9
    c_role = c_org + max(len(e["org"]) for e in exp) + 2
    c_arrow = c_role + max(len(e["role"]) for e in exp) + 2
    c_log = c_arrow + 2
    with_metric = [e for e in exp if e.get("metric")]
    c_metric = c_log + max(len(e["log"]) for e in with_metric) + 3
    for e in exp:
        cells = [
            (0, [(DIM, e["start"])]),
            (c_org, [(PLAIN, e["org"])]),
            (c_role, [(PLAIN, e["role"].lower())]),
            (c_arrow, [(DIM, "→")]),
            (c_log, [(PLAIN, e["log"])]),
        ]
        if e.get("metric"):
            cells.append((c_metric, [(AMB, e["metric"]), (PLAIN, f" {e['metric_note']}")]))
        out(cells, 0.09)
    blank()

    # builds
    projects = profile["projects"]
    command("ls builds/")
    rows = [projects[i:i + 3] for i in range(0, len(projects), 3)]
    for row in rows:
        out([(i * COL_PITCH, [(f"p:{p['color']}", p["repo"] + "/")]) for i, p in enumerate(row)])
    blank()

    # ci
    command("./ci --status", "# live from GitHub Actions, refreshed nightly")
    for row in rows:
        cells = []
        for i, p in enumerate(row):
            sym, cls = SYMBOL[statuses.get(p["repo"], ci.UNKNOWN)]
            cells.append((i * COL_PITCH, [(cls, sym), (PLAIN, " " + p["repo"])]))
        out(cells)
    blank()

    # open to
    command("./open-to --roles")
    o = profile["open_to"]
    summary = " · ".join([*o["roles"], str(o["start"]), o["where"]])
    out([(0, [(PR, "[ok]"), (PLAIN, " " + summary)])])
    lines.append(Line(cells=[(0, prompt)], kind="cursor", delay=clock[0]))
    return lines


def total_duration(lines: list[Line]) -> float:
    return max(line.delay + line.type_dur for line in lines)


def plain_summary(profile: dict[str, Any], statuses: dict[str, str], now: datetime) -> str:
    """The terminal as plain prose, used for alt text and the SVG description."""
    offset = utc_offset_label(now, profile["timezone"])
    o = profile["open_to"]
    parts = [
        f"{profile['name']}, {profile['tagline']}.",
        f"{profile['education']}.",
        f"Based in {profile['location']}, time zone {profile['timezone']} ({offset}).",
        "Experience: " + "; ".join(
            f"{e['org_full']}, {e['role']} ({e['year']}): {e['log']}"
            + (f", {e['metric']} {e['metric_note']}" if e.get("metric") else "")
            for e in profile["experience"]
        ) + ".",
        "Builds: " + ", ".join(p["repo"] for p in profile["projects"]) + ".",
    ]
    words = {ci.OK: "passing", ci.FAIL: "failing", ci.UNKNOWN: "status unknown"}
    parts.append("Latest CI: " + ", ".join(
        f"{p['repo']} {words[statuses.get(p['repo'], ci.UNKNOWN)]}" for p in profile["projects"]
    ) + ".")
    parts.append(
        f"Open to {', '.join(o['roles'])} roles starting {o['start']}, {o['where']}."
    )
    return " ".join(parts)


def _runs_markup(runs: list[Run]) -> str:
    out = []
    for cls, text in runs:
        if cls.startswith("p:"):
            out.append(f'<tspan fill="{cls[2:].upper()}">{esc(text)}</tspan>')
        elif cls:
            out.append(f'<tspan class="{cls}">{esc(text)}</tspan>')
        else:
            out.append(esc(text))
    return "".join(out)


def render_terminal(
    profile: dict[str, Any], statuses: dict[str, str], now: datetime, scheme: str
) -> str:
    lines = build_lines(profile, statuses, now)
    host = profile["location"].split(",")[0].strip().lower()
    n = len(lines)
    height = BAR_H + PAD_T + LH * n + PAD_B
    border = DARK["border"] if scheme == "dark" else LIGHT["border"]
    t = TERMINAL
    summary = plain_summary(profile, statuses, now)
    cover_right = WIDTH - 2

    body: list[str] = []
    cursor = ""
    for i, line in enumerate(lines):
        if line.kind == "blank":
            continue
        y = BAR_H + PAD_T + LH * i + 16
        texts = []
        for col, runs in line.cells:
            if line.kind == "prompt" and col == line.type_col:
                continue
            texts.append(
                f'<text x="{num(PAD_X + col * CW)}" y="{y}" xml:space="preserve">'
                f"{_runs_markup(runs)}</text>"
            )
        delay = f"{line.delay:.2f}s"
        if line.kind == "cursor":
            plen = sum(len(tx) for _, tx in line.cells[0][1])
            cx = PAD_X + plen * CW
            cursor = (
                f'<g class="a" style="animation-delay:{delay}">{"".join(texts)}'
                f'<rect class="cur" x="{num(cx)}" y="{y - 12}" width="8" height="15" '
                f'fill="{t["amber"]}"/></g>'
            )
            continue
        group = [f'<g class="a" style="animation-delay:{delay}">{"".join(texts)}</g>']
        if line.kind == "prompt":
            x0 = PAD_X + line.type_col * CW
            cmd_runs = next(r for c, r in line.cells if c == line.type_col)
            steps = max(1, round((cover_right - x0) / CW))
            tdelay = f"{line.delay + 0.1:.2f}s"
            group.append(
                f'<text x="{num(x0)}" y="{y}" xml:space="preserve">{_runs_markup(cmd_runs)}</text>'
                f'<rect class="t" transform="scale(0)" x="{num(x0 - 1)}" y="{y - 15}" width="{num(cover_right - x0 + 1)}" '
                f'height="{LH}" fill="{t["bg"]}" style="transform-origin:{cover_right}px 0;'
                f"animation-delay:{tdelay};animation-duration:{line.type_dur:.2f}s;"
                f'animation-timing-function:steps({steps},end)"/>'
            )
            # The command only appears once its prompt has; hide it until then.
            group[1:] = [f'<g class="a" style="animation-delay:{delay}">{"".join(group[1:])}</g>']
        body.append("".join(group))
    body.append(cursor)

    css = f"""
text{{font-family:{MONO};font-size:{FONT}px;fill:{t["fg"]}}}
.bt{{font-size:11.5px;fill:{t["dim"]}}}
.pr{{fill:{t["ok"]}}}.pa{{fill:{t["blue"]}}}.c{{fill:{t["amber"]}}}.d{{fill:{t["dim"]}}}
.h{{fill:{t["white"]};font-weight:600}}.am{{fill:{t["amber"]}}}
.ok{{fill:{STATUS["ok"]}}}.bad{{fill:{STATUS["fail"]}}}
@keyframes fi{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes ty{{from{{transform:scaleX(1)}}to{{transform:scaleX(0)}}}}
@keyframes bl{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
.a{{animation:fi .12s linear both}}
.t{{transform:scaleX(0);animation:ty 1s steps(10,end) both}}
.cur{{animation:bl 1.1s steps(1) infinite}}
@media (prefers-reduced-motion:reduce){{.a,.t,.cur{{animation:none}}}}
"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-label={attr(summary)}>
<title>Terminal introduction for {esc(profile["name"])}</title>
<desc>{esc(summary)}</desc>
<style>{css}</style>
<defs><clipPath id="w"><rect width="{WIDTH}" height="{height}" rx="8"/></clipPath></defs>
<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="8" fill="{t["bg"]}" stroke="{norm(border)}"/>
<g clip-path="url(#w)"><rect width="{WIDTH}" height="{BAR_H}" fill="{t["bar"]}"/><rect y="{BAR_H}" width="{WIDTH}" height="1" fill="{t["line"]}"/></g>
<text x="{PAD_X}" y="22" class="bt">{esc(f"{SHELL_USER}@{host}: ~")}</text>
<text x="{WIDTH - PAD_X}" y="22" text-anchor="end" class="bt">zsh · 96×24</text>
{"".join(body)}
</svg>
"""
