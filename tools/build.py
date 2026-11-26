#!/usr/bin/env python3
"""Sync shared files into every skill, check the plugin, and package it.

    python3 tools/build.py            sync, check, write dist/qc-webull-desk.plugin
    python3 tools/build.py --check    fail if any generated copy is stale; write nothing

Each skill must work on its own once installed, so shared files are copied in
rather than referenced across folders. `shared/` and `partner.json` are the
sources; the copies inside `skills/` are generated.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "shared"
SKILLS = ROOT / "skills"
NO_REPORT = {"start", "connect-webull"}
BARS = {"sector-rotation", "event-study"}
PACKAGE = ("README.md", "LICENSE", "NOTICE.md", "partner.json")
PLACEHOLDERS = {"DESK_NAME": "desk_name", "PARTNER_NAME": "partner_name", "REFERRAL_URL": "referral_url",
                "AGENTIC_URL": "agentic_url", "CLAUDE_CONNECTOR_URL": "claude_connector_url",
                "DISCLOSURE_TH": "disclosure_th", "DISCLOSURE_EN": "disclosure_en"}


def partner() -> dict:
    data = json.loads((ROOT / "partner.json").read_text(encoding="utf-8"))
    for key in set(PLACEHOLDERS.values()) | {"footer_th", "footer_en", "show_in_report_footer"}:
        if key not in data or data[key] == "":
            raise SystemExit(f"partner.json: {key} is missing")
    if not str(data["referral_url"]).startswith("https://www.webull.co.th/"):
        raise SystemExit("partner.json: referral_url must be an https://www.webull.co.th/ link")
    return data


def desk_rules(data: dict) -> str:
    text = (SHARED / "desk-rules.md").read_text(encoding="utf-8")
    for token, key in PLACEHOLDERS.items():
        text = text.replace("{{" + token + "}}", str(data[key]))
    left = re.findall(r"\{\{[A-Z_]+\}\}", text)
    if left:
        raise SystemExit(f"desk-rules.md: unknown placeholders {sorted(set(left))}")
    return text


def plan(data: dict) -> dict[Path, str]:
    """Every generated file and the text it must hold."""
    rules = desk_rules(data)
    render = (SHARED / "render_report.py").read_text(encoding="utf-8")
    bars = (SHARED / "bars_io.py").read_text(encoding="utf-8")
    card = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    out: dict[Path, str] = {}
    for skill in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        out[skill / "references" / "desk-rules.md"] = rules
        if skill.name not in NO_REPORT:
            out[skill / "scripts" / "render_report.py"] = render
            out[skill / "assets" / "partner.json"] = card
        if skill.name in BARS:
            out[skill / "scripts" / "bars_io.py"] = bars
    return out


def check(data: dict) -> list[str]:
    problems = []
    for skill in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        path = skill / "SKILL.md"
        if not path.exists():
            problems.append(f"{skill.name}: SKILL.md is missing")
            continue
        text = path.read_text(encoding="utf-8")
        head = re.match(r"---\n(.*?)\n---\n", text, re.S)
        if not head:
            problems.append(f"{skill.name}: no frontmatter")
            continue
        name = re.search(r"^name:\s*(.+)$", head.group(1), re.M)
        desc = re.search(r"^description:\s*(.+)$", head.group(1), re.M)
        if not name or name.group(1).strip() != skill.name:
            problems.append(f"{skill.name}: frontmatter name must equal the folder name")
        if not desc or len(desc.group(1)) < 80:
            problems.append(f"{skill.name}: description is missing or too short to route on")
        if "references/desk-rules.md" not in text:
            problems.append(f"{skill.name}: SKILL.md does not load references/desk-rules.md")
        for script in re.findall(r"scripts/([a-z_]+\.py)", text):
            if not (skill / "scripts" / script).exists() and script != "render_report.py":
                problems.append(f"{skill.name}: SKILL.md names scripts/{script}, which does not exist")
        if data["referral_url"] in text:
            problems.append(f"{skill.name}: the referral link belongs in partner.json, not in SKILL.md")
    menu = (SKILLS / "start" / "SKILL.md").read_text(encoding="utf-8")
    for skill in sorted(p.name for p in SKILLS.iterdir() if p.is_dir()):
        if skill != "start" and f"`/{skill}`" not in menu:
            problems.append(f"start: the menu or routing table does not mention /{skill}")
    rules = desk_rules(data)
    for line in rules.splitlines():
        if data["referral_url"] in line and not line.startswith(">"):
            problems.append("desk-rules.md: the referral link appears outside the partner block")
    for lang in ("th", "en"):
        if data[f"disclosure_{lang}"] not in rules:
            problems.append(f"desk-rules.md: the {lang} disclosure sentence is missing")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if data["referral_url"] in readme and data["disclosure_th"] not in readme:
        problems.append("README.md: the referral link appears without its disclosure sentence")
    manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    for key in ("name", "version", "description"):
        if not manifest.get(key):
            problems.append(f"plugin.json: {key} is missing")
    return problems


def package(version: str) -> Path:
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    target = dist / "qc-webull-desk.plugin"
    skip = {"__pycache__", ".DS_Store"}
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(ROOT / ".claude-plugin" / "plugin.json", ".claude-plugin/plugin.json")
        for name in PACKAGE:
            archive.write(ROOT / name, name)
        for folder in ("skills", "examples"):
            for path in sorted((ROOT / folder).rglob("*")):
                if path.is_file() and not (set(path.parts) & skip) and path.suffix != ".pyc":
                    archive.write(path, path.relative_to(ROOT).as_posix())
    return target


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    data = partner()
    files = plan(data)
    stale = [p for p, text in files.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
    if args.check:
        problems = [f"stale generated file: {p.relative_to(ROOT)}" for p in stale] + check(data)
        for line in problems:
            print(line, file=sys.stderr)
        print("ok" if not problems else f"{len(problems)} problem(s)")
        return 1 if problems else 0
    for path in stale:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(files[path], encoding="utf-8")
    problems = check(data)
    for line in problems:
        print(line, file=sys.stderr)
    if problems:
        print(f"{len(problems)} problem(s); nothing packaged")
        return 1
    manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    target = package(manifest["version"])
    print(f"synced {len(stale)} file(s); packaged {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
