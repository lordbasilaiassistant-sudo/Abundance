#!/usr/bin/env python3
"""Repo self-check: run before opening a PR. Standard library only.

    python3 scripts/check.py

Verifies the invariants that keep this site honest and unbroken:

  1. Every data/*.json parses, and every fact entry carries a primary-source URL.
  2. Every internal link/href/src in the HTML and Markdown resolves to a file
     that exists (external http(s) links are not fetched).
  3. Every <loc> in sitemap.xml maps to a file that exists.
  4. Every published page is listed in sitemap.xml.

Exit code 0 = clean, 1 = problems found (each printed as path: message).
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE_BASE = "https://lordbasilaiassistant-sudo.github.io/Abundance/"

# Keys that are metadata about the file, not fact entries needing a citation.
META_KEYS = {"$schema", "fetched_at", "source", "license", "indicators", "note", "notes"}
# Files exempt from the "must be in sitemap" rule (not public reading pages).
SITEMAP_EXEMPT = {"embed/calculator.html", "lang/es/index.html", "index.html"}

problems: list[str] = []


def problem(where: str, message: str) -> None:
    problems.append(f"{where}: {message}")


def check_data() -> None:
    """Every number on the site lives in data/*.json and must cite a source."""
    for path in sorted((ROOT / "data").glob("*.json")):
        rel = path.relative_to(ROOT).as_posix()
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problem(rel, f"invalid JSON — {exc}")
            continue
        if not isinstance(payload, dict):
            problem(rel, "top level must be an object keyed by entry id")
            continue
        if "$schema" not in payload:
            problem(rel, "missing the $schema description string")
        # countries.json is generated wholesale by build_countries.py and cites
        # its source once at the top rather than per record.
        if path.name == "countries.json":
            continue
        for key, entry in payload.items():
            if key in META_KEYS or not isinstance(entry, dict):
                continue
            urls = [
                value
                for name, value in entry.items()
                if "source" in name or name.endswith("_url")
                if isinstance(value, str) and value.startswith("http")
            ]
            if not urls:
                problem(f"{rel} → {key}", "no primary-source URL (*_source_url / source_url)")
            if not any("year" in name or "date" in name for name in entry):
                problem(f"{rel} → {key}", "no year/date field — stale numbers must be detectable")


LINK_PATTERNS = (
    re.compile(r'(?:href|src)\s*=\s*"([^"]+)"'),          # HTML
    re.compile(r'\]\(([^)\s]+)\)'),                        # Markdown
)


def check_links() -> None:
    """Internal links must resolve. External links are left to the reader."""
    files = [p for p in ROOT.rglob("*.html") if ".git" not in p.parts]
    files += [p for p in ROOT.glob("*.md")] + [p for p in ROOT.rglob("*/*.md")]
    for path in sorted(set(files)):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        seen: set[str] = set()
        for pattern in LINK_PATTERNS:
            for raw in pattern.findall(text):
                target = raw.strip()
                if target in seen:
                    continue
                seen.add(target)
                if not target or target.startswith(("http://", "https://", "#", "mailto:", "data:", "//")):
                    continue
                # Documentation placeholders and strings built in JS are not links.
                if target == "..." or any(ch in target for ch in "{}+$`"):
                    continue
                target = unquote(urlparse(target).path)
                if not target:
                    continue
                resolved = (path.parent / target).resolve()
                if not resolved.exists():
                    problem(rel, f"broken internal link → {raw}")


def check_sitemap() -> None:
    sitemap = ROOT / "sitemap.xml"
    locs = re.findall(r"<loc>([^<]+)</loc>", sitemap.read_text(encoding="utf-8"))
    listed: set[str] = set()
    for loc in locs:
        if not loc.startswith(SITE_BASE):
            problem("sitemap.xml", f"URL outside the site base → {loc}")
            continue
        rel = loc[len(SITE_BASE):]
        path = ROOT / (rel or "index.html")
        if path.is_dir():
            path = path / "index.html"
        if not path.exists():
            problem("sitemap.xml", f"lists a file that does not exist → {rel or '/'}")
        listed.add(path.relative_to(ROOT).as_posix())

    published = [
        p.relative_to(ROOT).as_posix()
        for p in sorted(ROOT.rglob("*.html"))
        if ".git" not in p.parts
    ]
    for rel in published:
        if rel in SITEMAP_EXEMPT or rel in listed:
            continue
        problem("sitemap.xml", f"published page is not listed → {rel}")


def main() -> int:
    check_data()
    check_links()
    check_sitemap()
    if problems:
        print(f"{len(problems)} problem(s) found:\n")
        for line in problems:
            print(f"  {line}")
        return 1
    print("All checks passed: data cited, links resolve, sitemap complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
