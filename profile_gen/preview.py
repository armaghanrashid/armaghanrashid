"""Writes preview.html: the README at GitHub's content width, once per colour scheme.

GitHub resolves <picture> from the viewer's colour scheme; here each pane resolves it
itself (dark pane -> the dark <source>, light pane -> the <img>) so both can be seen at once.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

PICTURE = re.compile(r"<picture>(.*?)</picture>", re.S)

CSS = """
body{margin:0;font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif}
.pane{width:830px;box-sizing:border-box;padding:32px;margin:0 0 24px}
.dark{background:#0d1117;color:#f0f6fc;--bd:#3d444d;--sub:#151b23;--link:#4493f8}
.light{background:#fff;color:#1f2328;--bd:#d1d9e0;--sub:#f6f8fa;--link:#0969da}
.pane img{max-width:100%}
h3{font-size:20px;font-weight:600;margin:24px 0 16px;padding-bottom:7px;border-bottom:1px solid var(--bd)}
p{font-size:16px;margin:0 0 16px}a{color:var(--link);text-decoration:none}
table{border-collapse:collapse;margin:0 0 16px;display:block;overflow:auto;width:max-content;max-width:100%}
th,td{border:1px solid var(--bd);padding:6px 13px;text-align:left}
tr:nth-child(2n){background:var(--sub)}
.pane p[align=center]{margin:0 0 16px}
.label{font:12px ui-monospace,Menlo,monospace;opacity:.6;margin:0 0 8px}
"""


def resolve_pictures(markup: str, scheme: str) -> str:
    def pick(m: re.Match) -> str:
        inner = m.group(1)
        img = re.search(r"<img[^>]*>", inner).group(0)
        if scheme == "dark":
            src = re.search(r'srcset="([^"]+)"', inner).group(1)
            img = re.sub(r'src="[^"]*"', f'src="{src}"', img, count=1)
        return img

    return PICTURE.sub(pick, markup)


def inline(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)


def md_to_html(md: str) -> str:
    out = []
    for block in re.split(r"\n\s*\n", md.strip()):
        if block.startswith("<!--"):
            continue
        if block.startswith("<"):
            out.append(block)
        elif block.startswith("### "):
            out.append(f"<h3>{html.escape(block[4:])}</h3>")
        elif block.startswith("|"):
            rows = [r for r in block.splitlines() if not re.fullmatch(r"\|[\s:|-]+\|", r)]
            cells = [[c.strip() for c in re.split(r"(?<!\\)\|", r.strip())[1:-1]] for r in rows]
            head = "".join(f"<th>{c}</th>" for c in cells[0])
            body = "".join(
                "<tr>" + "".join(f"<td>{inline(c.replace(chr(92) + '|', '|'))}</td>" for c in r)
                + "</tr>" for r in cells[1:]
            )
            out.append(f"<table><tr>{head}</tr>{body}</table>")
        else:
            out.append(f"<p>{inline(block)}</p>")
    return "\n".join(out)


def build_preview(root: Path) -> Path:
    md = (root / "README.md").read_text(encoding="utf-8")
    panes = []
    for scheme in ("dark", "light"):
        body = md_to_html(resolve_pictures(md, scheme))
        panes.append(f'<div class="pane {scheme}"><div class="label">GitHub {scheme}</div>{body}</div>')
    page = (
        '<!doctype html><meta charset="utf-8"><title>preview</title>'
        f"<style>{CSS}</style>" + "\n".join(panes)
    )
    out = root / "preview.html"
    out.write_text(page, encoding="utf-8")
    return out


if __name__ == "__main__":
    print(build_preview(Path(__file__).resolve().parent.parent))
