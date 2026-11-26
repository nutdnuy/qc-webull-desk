#!/usr/bin/env python3
"""Render a desk report (JSON) into one self-contained HTML page.

Usage:
    python3 render_report.py report.json --out report.html [--no-partner]
    python3 render_report.py report.json --check

Standard library only. The JSON contract is in references/desk-rules.md.
Generated copy: edit shared/render_report.py and run tools/build.py.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

PAPER = "#F4F2EB"
INK = "#1D1D1B"
GREEN = "#173C2C"
SIGNAL = "#1E8E63"
GREY = "#8C8B84"
FIGURE_TYPES = ("table", "bars", "line", "scatter")
LABELS = {
    "th": {"source": "แหล่งข้อมูล", "period": "ช่วงเวลา", "unit": "หน่วย", "limits": "ข้อจำกัด",
           "sources": "แหล่งอ้างอิง", "as_of": "ข้อมูล ณ",
           "disclaimer": "เนื้อหานี้เป็นข้อมูลและผลการวิเคราะห์เพื่อประกอบการตัดสินใจของคุณเอง ไม่ใช่คำแนะนำการลงทุน "
                         "ผลลัพธ์จาก AI อาจผิดพลาดหรือตกหล่น ควรตรวจตัวเลขกับแหล่งข้อมูลต้นทางก่อนตัดสินใจ "
                         "ผลการดำเนินงานในอดีตไม่ได้ยืนยันผลในอนาคต ปลั๊กอินนี้จัดทำโดย QuantCorner "
                         "ไม่ใช่ผลิตภัณฑ์หรือบทวิเคราะห์ของ Webull"},
    "en": {"source": "Source", "period": "Period", "unit": "Unit", "limits": "Limits",
           "sources": "Sources", "as_of": "Data as of",
           "disclaimer": "This page is information and analysis for your own decision. It is not investment advice. "
                         "AI output can contain errors or omissions, so check figures against the original source "
                         "before acting. Past performance does not indicate future results. This plugin is made by "
                         "QuantCorner. It is not a Webull product or Webull research."},
}

CSS = """
:root{--qc-paper:#F4F2EB;--qc-ink:#1D1D1B;--qc-press-green:#173C2C;--qc-grey-text:#5E5D57;--qc-grey-on-green:#AEB9B1;
--qc-font-headline-en:"Newsreader";--qc-font-headline-th:"Noto Serif Thai";--qc-font-body-th:"IBM Plex Sans Thai Looped";--qc-font-mono:"IBM Plex Mono"}
*{box-sizing:border-box}
body{margin:0;background:var(--qc-paper);color:var(--qc-ink);font-family:var(--qc-font-headline-en),var(--qc-font-body-th);font-size:17px;line-height:1.6}
[lang=th]{font-family:var(--qc-font-body-th);line-height:1.7}
.band{background:var(--qc-press-green);color:var(--qc-paper);padding:20px 6vw;display:flex;flex-wrap:wrap;gap:6px 32px;justify-content:space-between;align-items:baseline}
.band p{margin:0;font-family:var(--qc-font-body-th);font-weight:500;font-size:13px;line-height:1.5}
.band .meta{color:var(--qc-grey-on-green)}
main,footer{max-width:920px;margin:0 auto;padding:0 6vw}
h1{margin:40px 0 20px;font-weight:600}
h1 span{display:block;font-size:clamp(28px,5vw,40px)}
h1 [data-qc=headline-en]{font-family:var(--qc-font-headline-en);font-weight:600;line-height:1.12}
h1 [data-qc=headline-th]{font-family:var(--qc-font-headline-th);font-weight:700;line-height:1.36;margin-top:6px}
.answer{font-size:clamp(19px,2.6vw,23px);line-height:1.5;margin:0 0 28px;padding-bottom:28px;border-bottom:3px solid var(--qc-ink)}
.answer[lang=th]{line-height:1.6}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:0 24px;margin:0 0 12px}
.kpi{border-top:1px solid var(--qc-ink);padding:12px 0 16px}
.kpi .label,.kpi .note{display:block;font-family:var(--qc-font-body-th);font-size:13px;line-height:1.5;color:var(--qc-grey-text)}
.kpi .label{font-weight:500;color:var(--qc-ink)}
.kpi .value{display:block;font-family:var(--qc-font-mono);font-weight:500;font-size:26px;line-height:1.3}
section{margin:36px 0}
h2{font-family:var(--qc-font-headline-en),var(--qc-font-headline-th);font-weight:600;font-size:clamp(22px,3.4vw,30px);line-height:1.35;margin:0 0 12px;padding-top:12px;border-top:1px solid var(--qc-ink)}
h2[lang=th]{font-family:var(--qc-font-headline-th);font-weight:500;line-height:1.5}
h3{font-family:var(--qc-font-body-th);font-weight:500;font-size:17px;margin:0 0 8px}
p{margin:0 0 12px}
ul{margin:0 0 12px;padding-left:20px}
li{margin:0 0 6px}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:0 28px}
.cols>div{border-top:3px solid var(--qc-ink);padding-top:10px}
figure{margin:0}
svg{display:block;width:100%;height:auto}
svg text{font-family:var(--qc-font-body-th);font-size:13px;fill:var(--qc-ink)}
svg text.num{font-family:var(--qc-font-mono)}
svg text.dim{fill:var(--qc-grey-text)}
.scroll{overflow-x:auto}
.wide svg{min-width:560px}
.bars{display:grid;grid-template-columns:fit-content(38%) 1fr max-content;gap:8px 12px;align-items:center;font-family:var(--qc-font-body-th);font-size:13px;line-height:1.4}
.bars .track{position:relative;height:18px;display:block}
.bars .zero{position:absolute;top:-4px;bottom:-4px;width:1px;background:var(--qc-ink)}
.bars .bar{position:absolute;top:0;bottom:0;background:var(--qc-ink)}
.bars .bar.pick{background:var(--qc-press-green)}
.bars .dot{position:absolute;top:50%;width:14px;height:14px;margin:-7px 0 0 -7px}
.bars .val{font-family:var(--qc-font-mono);text-align:right}
table{border-collapse:collapse;width:100%;font-family:var(--qc-font-body-th);font-size:15px;line-height:1.5}
th{font-weight:500;font-size:13px;text-align:left;border-bottom:3px solid var(--qc-ink);padding:8px 12px 8px 0;vertical-align:bottom}
td{border-bottom:1px solid var(--qc-ink);padding:8px 12px 8px 0;vertical-align:top}
.num{text-align:right;font-variant-numeric:tabular-nums;font-family:var(--qc-font-mono)}
th.num{font-family:var(--qc-font-body-th)}
.qc-source{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:4px 24px;margin:10px 0 0;padding-top:8px;border-top:1px solid var(--qc-ink);font-family:var(--qc-font-body-th);font-size:13px;line-height:1.5}
.qc-source dt{font-weight:500}
.qc-source dd{margin:0;color:var(--qc-grey-text)}
.limits{font-family:var(--qc-font-body-th);font-size:13px;line-height:1.5;color:var(--qc-grey-text);margin:6px 0 0}
footer{margin-top:48px;padding-top:16px;padding-bottom:48px;border-top:3px solid var(--qc-ink);font-family:var(--qc-font-body-th);font-size:13px;line-height:1.6;color:var(--qc-grey-text)}
footer p{margin:0 0 10px}
a{color:var(--qc-ink)}
@media print{.band{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500'
         '&family=IBM+Plex+Sans+Thai+Looped:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,600'
         '&family=Noto+Serif+Thai:wght@500;700&display=swap">')


class ReportError(ValueError):
    """The report JSON breaks the contract."""


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def is_thai(text) -> bool:
    return any("฀" <= ch <= "๿" for ch in str(text))


def lang_attr(text) -> str:
    return ' lang="th"' if is_thai(text) else ""


def num(value, where: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        raise ReportError(f"{where}: {value!r} is not a number")
    if out != out or out in (float("inf"), float("-inf")):
        raise ReportError(f"{where}: {value!r} is not finite")
    return out


def fmt(value: float, decimals: int = 2, suffix: str = "") -> str:
    return f"{value:,.{decimals}f}{suffix}"


class Page:
    def __init__(self, lang: str):
        self.lang = lang if lang in LABELS else "en"
        self.words = LABELS[self.lang]
        self.signal_used = False

    def take_signal(self) -> bool:
        if self.signal_used:
            return False
        self.signal_used = True
        return True

    def source_line(self, section: dict, where: str) -> str:
        src = section.get("source")
        if not isinstance(src, dict):
            raise ReportError(f"{where}: a figure needs source {{source, period, unit}}")
        parts = []
        for key in ("source", "period", "unit"):
            if not str(src.get(key, "")).strip():
                raise ReportError(f"{where}: source.{key} is missing")
            parts.append(f'<div><dt{lang_attr(self.words[key])}>{esc(self.words[key])}</dt>'
                         f'<dd{lang_attr(src[key])}>{esc(src[key])}</dd></div>')
        out = f'<dl class="qc-source" data-qc="source-line">{"".join(parts)}</dl>'
        if section.get("limits"):
            text = f'{self.words["limits"]}: {section["limits"]}'
            out += f'<p class="limits"{lang_attr(text)}>{esc(text)}</p>'
        return out


def signal_dot(x: float, y: float) -> str:
    return f'<circle data-qc="signal-point" cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{SIGNAL}"/>'


def html_bars(page: Page, s: dict, where: str) -> str:
    """Bars as HTML, so labels keep their size on a phone."""
    items = s.get("items") or []
    if not items:
        raise ReportError(f"{where}: bars need items")
    decimals, suffix = int(s.get("decimals", 2)), str(s.get("suffix", ""))
    vals = [num(i.get("value"), f"{where} item {n}") for n, i in enumerate(items)]
    lo, hi = min(0.0, min(vals)), max(0.0, max(vals))
    span = (hi - lo) or 1.0
    zero = 100 * (0 - lo) / span
    out = [f'<div class="bars" role="img" aria-label="{esc(s.get("heading", "Bars"))}">']
    for item, value in zip(items, vals):
        end = 100 * (value - lo) / span
        left, width = min(zero, end), max(abs(end - zero), 0.4)
        chosen = str(item.get("label")) == str(s.get("highlight"))
        label = str(item.get("label", ""))
        dot = ""
        if chosen and page.take_signal():
            dot = (f'<svg class="dot" style="left:{end:.2f}%" viewBox="0 0 14 14" aria-hidden="true">'
                   f'<circle data-qc="signal-point" cx="7" cy="7" r="7" fill="{SIGNAL}"/></svg>')
        out.append(f'<span{lang_attr(label)}>{esc(label)}</span><span class="track">'
                   f'<span class="zero" style="left:{zero:.2f}%"></span>'
                   f'<span class="bar{" pick" if chosen else ""}" style="left:{left:.2f}%;width:{width:.2f}%"></span>{dot}</span>'
                   f'<span class="val">{esc(fmt(value, decimals, suffix))}</span>')
    out.append("</div>")
    return "".join(out)


def svg_line(page: Page, s: dict, where: str) -> str:
    series = s.get("series") or []
    if not series or not series[0].get("points"):
        raise ReportError(f"{where}: line needs series with points")
    decimals = int(s.get("decimals", 2))
    data = []
    for n, one in enumerate(series):
        pts = [(str(p[0]), num(p[1], f"{where} series {n}")) for p in one.get("points", [])]
        if len(pts) < 2:
            raise ReportError(f"{where}: series {n} needs at least two points")
        data.append((str(one.get("name", "")), pts))
    ys = [y for _, pts in data for _, y in pts]
    lo, hi = min(ys), max(ys)
    pad = (hi - lo) * 0.08 or abs(hi) * 0.05 or 1.0
    lo, hi = lo - pad, hi + pad
    width, height, left, right, top, bottom = 720, 320, 64, 130, 14, 34
    longest = max(len(pts) for _, pts in data)

    def px(i: int, count: int) -> float:
        return left + (width - left - right) * (i / max(count - 1, 1)) * ((count - 1) / max(longest - 1, 1))

    def py(v: float) -> float:
        return top + (height - top - bottom) * (1 - (v - lo) / (hi - lo))

    out = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{esc(s.get("heading", "Line"))}">']
    for tick in (lo + pad, (lo + hi) / 2, hi - pad):
        out.append(f'<line x1="{left}" y1="{py(tick):.1f}" x2="{left - 6}" y2="{py(tick):.1f}" stroke="{INK}" stroke-width="1"/>')
        out.append(f'<text class="num dim" x="{left - 10}" y="{py(tick) + 4:.1f}" text-anchor="end">{esc(fmt(tick, decimals))}</text>')
    out.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height - bottom}" stroke="{INK}" stroke-width="1"/>')
    out.append(f'<line x1="{left}" y1="{height - bottom}" x2="{width - right}" y2="{height - bottom}" stroke="{INK}" stroke-width="1"/>')
    for n in range(len(data) - 1, -1, -1):
        name, pts = data[n]
        path = " ".join(f"{px(i, len(pts)):.1f},{py(y):.1f}" for i, (_, y) in enumerate(pts))
        colour, weight = (INK, 3) if n == 0 else (GREY, 2)
        out.append(f'<polyline points="{path}" fill="none" stroke="{colour}" stroke-width="{weight}" stroke-linejoin="round"/>')
        ex, ey = px(len(pts) - 1, len(pts)), py(pts[-1][1])
        out.append(f'<text x="{ex + 12:.1f}" y="{ey + 4:.1f}"{lang_attr(name)}>{esc(name)}</text>')
    main = data[0][1]
    idx = s.get("highlight_index")
    if idx is not None or s.get("highlight"):
        idx = len(main) - 1 if idx is None else max(0, min(int(idx), len(main) - 1))
        if page.take_signal():
            out.append(signal_dot(px(idx, len(main)), py(main[idx][1])))
    out.append(f'<text class="dim" x="{left}" y="{height - 10}">{esc(main[0][0])}</text>')
    out.append(f'<text class="dim" x="{width - right}" y="{height - 10}" text-anchor="end">{esc(main[-1][0])}</text>')
    out.append("</svg>")
    return "".join(out)


def svg_scatter(page: Page, s: dict, where: str) -> str:
    points = s.get("points") or []
    if not points:
        raise ReportError(f"{where}: scatter needs points")
    centre = s.get("centre") or [0, 0]
    cx0, cy0 = num(centre[0], where), num(centre[1], where)
    pts = [(str(p.get("label", "")), num(p.get("x"), where), num(p.get("y"), where)) for p in points]
    rx = max(abs(x - cx0) for _, x, _ in pts) * 1.25 or 1.0
    ry = max(abs(y - cy0) for _, _, y in pts) * 1.25 or 1.0
    width, height, left, right, top, bottom = 720, 440, 20, 20, 28, 40

    def px(x: float) -> float:
        return left + (width - left - right) * ((x - (cx0 - rx)) / (2 * rx))

    def py(y: float) -> float:
        return top + (height - top - bottom) * (1 - (y - (cy0 - ry)) / (2 * ry))

    out = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{esc(s.get("heading", "Scatter"))}">',
           f'<line x1="{left}" y1="{py(cy0):.1f}" x2="{width - right}" y2="{py(cy0):.1f}" stroke="{INK}" stroke-width="1"/>',
           f'<line x1="{px(cx0):.1f}" y1="{top}" x2="{px(cx0):.1f}" y2="{height - bottom}" stroke="{INK}" stroke-width="1"/>']
    names = (s.get("quadrants") or []) + ["", "", "", ""]
    corners = ((left, top - 10, "start"), (width - right, top - 10, "end"),
               (left, height - bottom + 16, "start"), (width - right, height - bottom + 16, "end"))
    for name, (x, y, anchor) in zip(names, corners):
        if name:
            out.append(f'<text class="dim" x="{x}" y="{y}" text-anchor="{anchor}"{lang_attr(name)}>{esc(name)}</text>')
    if s.get("x_label"):
        out.append(f'<text class="dim" x="{width / 2}" y="{height - 6}" text-anchor="middle"{lang_attr(s["x_label"])}>{esc(s["x_label"])}</text>')
    if s.get("y_label"):
        out.append(f'<text class="dim" x="{px(cx0) + 8:.1f}" y="{top + 12}"{lang_attr(s["y_label"])}>{esc(s["y_label"])}</text>')
    for label, x, y in pts:
        chosen = label == str(s.get("highlight"))
        if chosen and page.take_signal():
            out.append(signal_dot(px(x), py(y)))
        else:
            out.append(f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="5" fill="{GREEN if chosen else INK}"/>')
        flip = px(x) > width - 110
        anchor = ' text-anchor="end"' if flip else ""
        out.append(f'<text x="{px(x) + (-10 if flip else 10):.1f}" y="{py(y) + 4:.1f}"{anchor}>{esc(label)}</text>')
    out.append("</svg>")
    return "".join(out)


def html_table(s: dict, where: str) -> str:
    cols, rows = s.get("columns") or [], s.get("rows") or []
    if not cols or not rows:
        raise ReportError(f"{where}: table needs columns and rows")
    numeric = set(int(i) for i in s.get("numeric", []))
    def cls(i: int) -> str:
        return ' class="num"' if i in numeric else ""

    head = "".join(f'<th scope="col"{cls(i)}{lang_attr(c)}>{esc(c)}</th>' for i, c in enumerate(cols))
    body = []
    for r, row in enumerate(rows):
        if len(row) != len(cols):
            raise ReportError(f"{where}: row {r} has {len(row)} cells for {len(cols)} columns")
        body.append("<tr>" + "".join(f'<td{cls(i)}{lang_attr(c)}>{esc(c)}</td>' for i, c in enumerate(row)) + "</tr>")
    return f'<div class="scroll"><table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def wide(svg: str) -> str:
    """Charts with text scroll sideways on a phone instead of shrinking."""
    return f'<div class="scroll wide">{svg}</div>'


def render_section(page: Page, s: dict, n: int) -> str:
    kind = s.get("type")
    where = f"section {n} ({kind})"
    out = ["<section>"]
    if s.get("heading"):
        out.append(f'<h2{lang_attr(s["heading"])}>{esc(s["heading"])}</h2>')
    if kind == "text":
        out += [f'<p{lang_attr(p)}>{esc(p)}</p>' for p in s.get("body", [])]
    elif kind == "list":
        out.append("<ul>" + "".join(f'<li{lang_attr(i)}>{esc(i)}</li>' for i in s.get("items", [])) + "</ul>")
    elif kind == "columns":
        out.append('<div class="cols">')
        for col in s.get("columns", []):
            items = "".join(f'<li{lang_attr(i)}>{esc(i)}</li>' for i in col.get("items", []))
            out.append(f'<div><h3{lang_attr(col.get("title", ""))}>{esc(col.get("title", ""))}</h3><ul>{items}</ul></div>')
        out.append("</div>")
    elif kind in FIGURE_TYPES:
        inner = {"table": lambda: html_table(s, where), "bars": lambda: html_bars(page, s, where),
                 "line": lambda: wide(svg_line(page, s, where)),
                 "scatter": lambda: wide(svg_scatter(page, s, where))}[kind]()
        out.append(f'<figure data-qc="figure">{inner}</figure>{page.source_line(s, where)}')
    else:
        raise ReportError(f"{where}: unknown type; use text, list, columns, table, bars, line or scatter")
    out.append("</section>")
    return "".join(out)


def load_partner(script: Path) -> dict:
    path = script.parent.parent / "assets" / "partner.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def render(report: dict, partner: dict | None = None) -> str:
    for key in ("title_en", "title_th", "answer", "as_of"):
        if not str(report.get(key, "")).strip():
            raise ReportError(f"{key} is required")
    if is_thai(report["title_en"]) or not is_thai(report["title_th"]):
        raise ReportError("title_en must be English and title_th must be Thai")
    page = Page(str(report.get("lang", "th")))
    words = page.words
    partner = partner or {}
    desk = partner.get("desk_name", "QuantCorner Desk for Webull")
    as_of = f'{words["as_of"]} {report["as_of"]}'
    out = ['<!DOCTYPE html>', f'<html lang="{page.lang}"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width,initial-scale=1">',
           f'<title>{esc(report["title_en"])}</title>', FONTS, f'<style>{CSS}</style></head><body>',
           f'<header class="band" data-qc="band"><p>{esc(desk)}</p>'
           f'<p class="meta"{lang_attr(report.get("kicker", ""))}>{esc(report.get("kicker", ""))}</p>'
           f'<p class="meta"{lang_attr(as_of)}>{esc(as_of)}</p></header><main>',
           f'<h1><span data-qc="headline-en" lang="en">{esc(report["title_en"])}</span>'
           f'<span data-qc="headline-th" lang="th">{esc(report["title_th"])}</span></h1>',
           f'<p class="answer"{lang_attr(report["answer"])}>{esc(report["answer"])}</p>']
    kpis = report.get("kpis") or []
    if kpis:
        out.append('<div class="kpis">')
        for k in kpis:
            note = f'<span class="note"{lang_attr(k.get("note", ""))}>{esc(k["note"])}</span>' if k.get("note") else ""
            out.append(f'<div class="kpi"><span class="label"{lang_attr(k.get("label", ""))}>{esc(k.get("label", ""))}</span>'
                       f'<span class="value">{esc(k.get("value", ""))}</span>{note}</div>')
        out.append("</div>")
    for n, section in enumerate(report.get("sections") or []):
        out.append(render_section(page, section, n))
    if report.get("limits"):
        items = "".join(f'<li{lang_attr(i)}>{esc(i)}</li>' for i in report["limits"])
        out.append(f'<section><h2{lang_attr(words["limits"])}>{esc(words["limits"])}</h2><ul>{items}</ul></section>')
    out.append("</main><footer>")
    if report.get("sources"):
        def src(i: dict) -> str:
            text = str(i.get("label", "")) + (", " + str(i["detail"]) if i.get("detail") else "")
            return f'<li{lang_attr(text)}>{esc(text)}</li>'

        rows = "".join(src(i) for i in report["sources"])
        out.append(f'<p{lang_attr(words["sources"])}>{esc(words["sources"])}</p><ul>{rows}</ul>')
    out.append(f'<p{lang_attr(words["disclaimer"])}>{esc(words["disclaimer"])}</p>')
    if partner.get("show_in_report_footer") and partner.get("referral_url"):
        line = partner.get(f"footer_{page.lang}", "")
        note = partner.get(f"disclosure_{page.lang}", "")
        out.append(f'<p{lang_attr(line + note)}>{esc(line)} <a href="{esc(partner["referral_url"])}" rel="sponsored noopener">'
                   f'{esc(partner["referral_url"])}</a><br>{esc(note)}</p>')
    out.append("</footer></body></html>")
    return "".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Render a desk report JSON to HTML.")
    parser.add_argument("report", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", action="store_true", help="validate only")
    parser.add_argument("--no-partner", action="store_true", help="leave the referral line out of the footer")
    args = parser.parse_args(argv)
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
        partner = {} if args.no_partner else load_partner(Path(__file__).resolve())
        page = render(report, partner)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.check:
        print("ok")
        return 0
    out = args.out or args.report.with_suffix(".html")
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
