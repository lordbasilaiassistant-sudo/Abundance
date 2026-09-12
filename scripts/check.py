#!/usr/bin/env python3
"""Repo self-check: run before opening a PR. Standard library only.

    python3 scripts/check.py

Verifies the invariants that keep this site honest and unbroken:

  1. Every data/*.json parses, and every fact entry carries a primary-source URL.
  2. Every internal link/href/src in the HTML and Markdown resolves to a file
     that exists (external http(s) links are not fetched).
  3. Every <loc> in sitemap.xml maps to a file that exists.
  4. Every published page is listed in sitemap.xml and in llms.txt.
  5. Every published page carries the head metadata the site depends on
     (title, description, a self-referential canonical, OpenGraph, lang).
  6. The documentation still describes the repo: every script is in
     scripts/README.md, every stylesheet is actually loaded, and the data
     vintage in README.md matches data/countries.json.

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
# The embed is designed to live inside someone else's page: no canonical, no
# social card, and it is reached through the host document, not search.
METADATA_EXEMPT = {"embed/calculator.html"}

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


def published_pages() -> list[Path]:
    return [p for p in sorted(ROOT.rglob("*.html")) if ".git" not in p.parts]


def site_url_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel.endswith("index.html"):
        rel = rel[: -len("index.html")]
    return SITE_BASE + rel


def check_page_metadata() -> None:
    """Head metadata is how this page gets cited. Missing tags are defects."""
    required = {
        r"<title[^>]*>": "no <title>",
        r'name="description"': "no meta description",
        r'property="og:title"': "no og:title",
        r'property="og:image"': "no og:image",
    }
    for path in published_pages():
        rel = path.relative_to(ROOT).as_posix()
        if rel in METADATA_EXEMPT:
            continue
        head = path.read_text(encoding="utf-8", errors="replace").split("</head>")[0]
        for pattern, message in required.items():
            if not re.search(pattern, head, re.I):
                problem(rel, message)

        canonical = re.search(r'rel="canonical"[^>]*href="([^"]+)"', head, re.I)
        if not canonical:
            problem(rel, "no rel=canonical link")
        elif canonical.group(1) != site_url_for(path):
            problem(rel, f"canonical points elsewhere → {canonical.group(1)} (expected {site_url_for(path)})")

        lang = re.search(r"<html[^>]*\slang=\"([^\"]+)\"", head, re.I)
        if not lang:
            problem(rel, "<html> has no lang attribute")
        elif rel.startswith("lang/"):
            expected = rel.split("/")[1]
            if lang.group(1).split("-")[0] != expected:
                problem(rel, f'lang="{lang.group(1)}" does not match the lang/{expected}/ directory')


def check_llms_txt() -> None:
    """llms.txt is the agent-facing index; it must not drift from the site."""
    llms = ROOT / "llms.txt"
    if not llms.exists():
        problem("llms.txt", "missing — agents read this before the HTML")
        return
    text = llms.read_text(encoding="utf-8")
    listed = set(re.findall(re.escape(SITE_BASE) + r"([^)\s]*)", text))
    for path in published_pages():
        rel = path.relative_to(ROOT).as_posix()
        if rel in SITEMAP_EXEMPT and rel != "index.html":
            continue
        candidates = {rel, rel[: -len("index.html")] if rel.endswith("index.html") else rel}
        if not (candidates & listed):
            problem("llms.txt", f"published page is not indexed → {rel}")
    for rel in sorted(listed):
        target = ROOT / (rel or "index.html")
        if target.is_dir():
            target = target / "index.html"
        if not target.exists():
            problem("llms.txt", f"indexes a path that does not exist → {rel or '/'}")


def check_docs_match_repo() -> None:
    """Documentation drift is the failure mode this repo actually has."""
    scripts_readme = (ROOT / "scripts" / "README.md").read_text(encoding="utf-8")
    for script in sorted((ROOT / "scripts").glob("*.py")):
        if script.name not in scripts_readme:
            problem("scripts/README.md", f"undocumented script → scripts/{script.name}")

    loaded = ""
    for path in published_pages() + [ROOT / "style.css"]:
        loaded += path.read_text(encoding="utf-8", errors="replace")
    for sheet in sorted((ROOT / "styles").glob("*.css")):
        if sheet.name not in loaded:
            problem("styles/", f"stylesheet is never loaded by a page or style.css → styles/{sheet.name}")

    fetched_at = json.loads((ROOT / "data" / "countries.json").read_text(encoding="utf-8")).get("fetched_at")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    stated = re.search(r"Last refresh: \*\*([0-9]{4}-[0-9]{2}-[0-9]{2})\*\*", readme)
    if not stated:
        problem("README.md", "no 'Last refresh: **YYYY-MM-DD**' line in the Data currency section")
    elif fetched_at and stated.group(1) != fetched_at:
        problem(
            "README.md",
            f"Data currency says {stated.group(1)} but data/countries.json was fetched {fetched_at}",
        )


def main() -> int:
    check_data()
    check_links()
    check_sitemap()
    check_page_metadata()
    check_llms_txt()
    check_docs_match_repo()
    if problems:
        print(f"{len(problems)} problem(s) found:\n")
        for line in problems:
            print(f"  {line}")
        return 1
    print("All checks passed: data cited, links resolve, indexes and docs match the repo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
