# `scripts/` — regeneration utilities

All scripts are Python 3, standard-library where possible. Run them with the system Python (`py` on Windows, `python3` on macOS/Linux). They are idempotent — re-running produces the same output for the same inputs.

## Inventory

| Script | Output | Inputs | When to re-run |
|---|---|---|---|
| [`check.py`](check.py) | exit code + problem list | The repo itself | **Before every PR.** Verifies each `data/*.json` entry cites a primary source and a year, that internal links resolve, and that `sitemap.xml` matches the published pages. Standard library only. |
| [`check_sources.py`](check_sources.py) | report on stdout (`--json` for a file) | Every source URL in `data/*.json` (`--md` adds the Markdown docs) | On a schedule, and before a release. Hits the network, so it is deliberately outside `check.py` and CI. Splits findings into DEAD (404/410 — the citation rotted and the number is now unsourced) and INCONCLUSIVE (403/429 — the publisher blocks scripts; a human must open it). |
| [`build_landing.py`](build_landing.py) | `../index.html`, `../assets/planet.svg` | The template inside the script | When homepage markup or the illustration changes. Edit the script, never the generated files. |
| [`build_countries.py`](build_countries.py) | `../data/countries.json` | World Bank Open Data API (live HTTP) | When you add a country to the `COUNTRIES` list, or when World Bank publishes newer indicator vintages (annually). |
| [`apply_editorial.py`](apply_editorial.py) | Edits the reading pages in place | Its `pages` list | When you add a reading page, or change the shared editorial theme/nav. Idempotent — safe to re-run. |
| [`clean_vtt.py`](clean_vtt.py) | `../transcripts/{id}.txt` from `{id}.vtt` | A YouTube `.vtt` auto-caption file | When you add a new transcript. |
| [`make_og.py`](make_og.py) | `../og.png` (1200×630 social card) | Hardcoded headline math | When the headline numbers change. |
| [`make_og_letter.py`](make_og_letter.py) | `../og-letter.png` | Hardcoded copy | When the open letter's share card changes. |
| [`make_editorial_og.py`](make_editorial_og.py) | `../og-editorial.png` | Hardcoded design | When the editorial share card changes. **Uses Windows font paths** (`C:/Windows/Fonts/…`) — adjust before running elsewhere. |
| [`make_favicon.py`](make_favicon.py) | `../favicon.png` (32×32) + `../apple-touch-icon.png` (180×180) | Hardcoded design tokens | When branding changes (rare). |

[`landing.js`](landing.js) is not a script in this sense — it is the homepage's
client-side JavaScript, served to browsers and loaded by `index.html`.

## Dependencies

- `yt-dlp` (only if downloading a new transcript): `py -m pip install yt-dlp`
- `Pillow` (for image scripts): `py -m pip install Pillow`

Otherwise standard library only — `urllib.request`, `json`, `re`, `pathlib`.

## Conventions

- Each script writes to a deterministic path relative to repo root.
- No script takes command-line arguments; configuration lives at the top of the file as ALL-CAPS constants.
- Output files are committed alongside source changes; the scripts are documentation of how the artifacts were produced, not a build step that runs on deploy.
- If a script needs to be re-run as part of normal operation, that's noted in the task table in [`AGENTS.md`](../AGENTS.md#common-tasks).
- `check.py` is the exception to "no script takes arguments and each writes a file": it writes nothing and reports problems on stdout.
