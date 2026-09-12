#!/usr/bin/env python3
"""Record a Wayback Machine snapshot for every primary source.

    python3 scripts/archive_sources.py --dry-run       # report coverage, write nothing
    python3 scripts/archive_sources.py                 # record snapshots into data/*.json
    python3 scripts/archive_sources.py --save          # also ask Wayback to capture misses

Two citations in this repo rotted within a year. Vigilance does not scale;
archival does. For each `*_source_url` this asks the Wayback Machine for its
closest snapshot and stores it beside the original as `archived_url` (plus
`archived_at`, the snapshot's own date), so a 404 at the publisher degrades to
an inconvenience instead of an unsourced number.

The archived copy never replaces the citation. The publisher's URL stays
canonical; the snapshot is the fallback, and it is dated so a reader can see
what the page said when the figure was taken from it.

`--save` submits URLs with no snapshot to `web.archive.org/save`. That is slow
and heavily rate-limited, so it is opt-in and best run occasionally.
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = "AbundanceArchive/1.0 (+https://github.com/lordbasilaiassistant-sudo/Abundance)"
AVAILABILITY = "http://archive.org/wayback/available?url="
SAVE = "https://web.archive.org/save/"
# Keys whose value is a citation URL. Everything else in an entry is data.
SOURCE_KEYS = ("source_url", "primary_source_url")
PAUSE = 1.5  # archive.org rate-limits shared IPs hard; be a polite client.


def get_json(url: str, tries: int = 4) -> dict | None:
    """GET with backoff. archive.org answers 429 freely; that is not an error."""
    for attempt in range(tries):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except Exception:
            if attempt == tries - 1:
                return None
            time.sleep(2 * (attempt + 1))
    return None


def closest_snapshot(url: str) -> tuple[str, str] | None:
    """(snapshot url, YYYY-MM-DD) for the nearest capture, or None."""
    payload = get_json(AVAILABILITY + urllib.parse.quote(url, safe=""))
    if not payload:
        return None
    snapshot = (payload.get("archived_snapshots") or {}).get("closest")
    if not snapshot or not snapshot.get("available"):
        return None
    stamp = snapshot.get("timestamp", "")
    dated = f"{stamp[0:4]}-{stamp[4:6]}-{stamp[6:8]}" if len(stamp) >= 8 else ""
    # The API hands back http:// links; the site is https-only.
    return snapshot["url"].replace("http://web.archive.org", "https://web.archive.org"), dated


def request_capture(url: str) -> bool:
    try:
        request = urllib.request.Request(SAVE + url, headers={"User-Agent": UA})
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.status < 400
    except Exception:
        return False


def walk_entries(payload: dict):
    """Yield (entry_key, entry_dict) for every citable entry in a data file."""
    for key, entry in payload.items():
        if isinstance(entry, dict):
            yield key, entry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report coverage, write nothing")
    parser.add_argument("--save", action="store_true", help="ask Wayback to capture URLs with no snapshot")
    parser.add_argument("--file", help="limit to one data file, e.g. data/essentials.json")
    args = parser.parse_args()

    files = [ROOT / args.file] if args.file else sorted((ROOT / "data").glob("*.json"))
    recorded = missing = already = 0

    for path in files:
        if path.name == "countries.json":
            continue  # generated wholesale; cites its API once at the top
        payload = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for key, entry in walk_entries(payload):
            for source_key in SOURCE_KEYS:
                url = entry.get(source_key)
                if not isinstance(url, str) or not url.startswith("http"):
                    continue
                archived_key = "archived_url" if source_key == "source_url" else "primary_archived_url"
                if entry.get(archived_key):
                    already += 1
                    continue

                found = closest_snapshot(url)
                time.sleep(PAUSE)
                if not found and args.save:
                    print(f"  capturing {url}")
                    if request_capture(url):
                        time.sleep(PAUSE)
                        found = closest_snapshot(url)
                if not found:
                    missing += 1
                    print(f"  NO SNAPSHOT  {path.name} → {key}\n               {url}")
                    continue

                snapshot, dated = found
                print(f"  archived     {path.name} → {key}  ({dated})")
                recorded += 1
                if not args.dry_run:
                    # Insert right after the source URL so the pair reads together.
                    rebuilt = {}
                    for k, v in entry.items():
                        rebuilt[k] = v
                        if k == source_key:
                            rebuilt[archived_key] = snapshot
                            rebuilt[archived_key.replace("url", "at")] = dated
                    entry.clear()
                    entry.update(rebuilt)
                    changed = True

        if changed and not args.dry_run:
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"  wrote {path.relative_to(ROOT)}")

    print(
        f"\n{recorded} snapshot(s) recorded, {already} already had one, "
        f"{missing} with no capture on file."
    )
    if missing:
        print("Re-run with --save to ask the Wayback Machine to capture those.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
