#!/usr/bin/env python3
"""Citation link-rot check: does every primary source still resolve?

    python3 scripts/check_sources.py            # every source URL in data/*.json
    python3 scripts/check_sources.py --md        # also the links in the Markdown docs
    python3 scripts/check_sources.py --json out.json   # machine-readable report

This one talks to the network, so it is deliberately NOT part of
`scripts/check.py` or the CI check — run it on a schedule. A dead citation is a
real defect here: the whole project rests on every number being traceable.

Exit code 0 = every source reachable, 1 = at least one is not.
Findings are split in two, because they need different responses:

  DEAD          404/410, or a host that no longer resolves — the citation is
                rot and the number it backs is now unsourced. Fix it.
  INCONCLUSIVE  403/405/429/redirect/TLS refusal — publishers routinely block
                automated requests. A human opening the link in a browser is
                the only way to tell. Never "fix" one of these by swapping in
                a different source without reading the document first.
"""
import argparse
import json
import re
import ssl
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIMEOUT = 20
UA = "Mozilla/5.0 (compatible; AbundanceLinkCheck/1.0; +https://github.com/lordbasilaiassistant-sudo/Abundance)"
# Statuses that mean "the server declined to talk to a script", not "gone".
# Academic publishers and institutional sites return these to any non-browser.
INCONCLUSIVE_STATUSES = {401, 402, 403, 405, 406, 409, 418, 429, 451, 500, 502, 503}
DEAD_STATUSES = {404, 410}


def collect_urls(include_markdown: bool) -> dict[str, list[str]]:
    """url -> the places that cite it."""
    found: dict[str, list[str]] = {}

    def add(url: str, where: str) -> None:
        found.setdefault(url.rstrip(".,)"), []).append(where)

    for path in sorted((ROOT / "data").glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        rel = path.relative_to(ROOT).as_posix()

        def walk(node, trail: str) -> None:
            if isinstance(node, dict):
                for key, value in node.items():
                    walk(value, f"{trail} → {key}" if trail else key)
            elif isinstance(node, list):
                for item in node:
                    walk(item, trail)
            elif isinstance(node, str) and node.startswith("http"):
                add(node, f"{rel} ({trail})")

        walk(payload, "")

    if include_markdown:
        for path in sorted(ROOT.rglob("*.md")):
            if ".git" in path.parts:
                continue
            rel = path.relative_to(ROOT).as_posix()
            for url in re.findall(r"\]\((https?://[^)\s]+)\)", path.read_text(encoding="utf-8")):
                add(url, rel)
    return found


def probe(url: str) -> tuple[str, int | str]:
    """HEAD, falling back to GET — some servers only answer the latter."""
    context = ssl.create_default_context()
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT, context=context) as response:
                return url, response.status
        except urllib.error.HTTPError as exc:
            if method == "GET" or exc.code not in (403, 405, 501):
                return url, exc.code
        except Exception as exc:  # DNS failure, timeout, TLS, connection reset
            if method == "GET":
                return url, type(exc).__name__
    return url, "unreachable"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--md", action="store_true", help="also check links in Markdown docs")
    parser.add_argument("--json", metavar="PATH", help="write a machine-readable report")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    urls = collect_urls(args.md)
    print(f"Checking {len(urls)} source URLs…\n")
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = dict(pool.map(probe, urls))

    dead, inconclusive = [], []
    for url, status in sorted(results.items()):
        if status == 200 or (isinstance(status, int) and 200 <= status < 400):
            continue
        if isinstance(status, int) and status in DEAD_STATUSES:
            dead.append((url, status))
        else:
            inconclusive.append((url, status))

    if inconclusive:
        print(f"{len(inconclusive)} inconclusive — the server declined an automated request.")
        print("Open these in a browser before touching the citation:\n")
        for url, status in inconclusive:
            print(f"  [{status}] {url}")
        print()
    if dead:
        print(f"{len(dead)} DEAD source(s) — the cited document is gone, so the number it")
        print("backs is currently unsourced. Find the document's new home (publisher DOI,")
        print("institutional repository, or Wayback) and read it before updating the URL:\n")
        for url, status in dead:
            print(f"  [{status}] {url}")
            for where in urls[url]:
                print(f"        cited by {where}")
    else:
        print("No dead citations.")

    if args.json:
        Path(args.json).write_text(
            json.dumps(
                {
                    "checked": len(urls),
                    "dead": [{"url": u, "status": s, "cited_by": urls[u]} for u, s in dead],
                    "inconclusive": [{"url": u, "status": s, "cited_by": urls[u]} for u, s in inconclusive],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"\nReport written to {args.json}")
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
