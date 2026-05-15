# `scripts/` — regeneration utilities

All scripts are Python 3, standard-library where possible. Run them with the system Python (`py` on Windows, `python3` on macOS/Linux). They are idempotent — re-running produces the same output for the same inputs.

## Inventory

| Script | Output | Inputs | When to re-run |
|---|---|---|---|
| [`build_countries.py`](build_countries.py) | `../data/countries.json` | World Bank Open Data API (live HTTP) | When you add a country to the list, or when World Bank publishes newer indicator vintages (annually). |
| [`clean_vtt.py`](clean_vtt.py) | `../transcripts/{id}.txt` from `{id}.vtt` | A YouTube `.vtt` auto-caption file | When you add a new transcript. |
| [`make_og.py`](make_og.py) | `../og.png` (1200×630 social card) | Hardcoded headline math | When the headline numbers change. |
| [`make_favicon.py`](make_favicon.py) | `../favicon.png` (32×32) + `../apple-touch-icon.png` (180×180) | Hardcoded design tokens | When branding changes (rare). |

## Dependencies

- `yt-dlp` (only if downloading a new transcript): `py -m pip install yt-dlp`
- `Pillow` (for image scripts): `py -m pip install Pillow`

Otherwise standard library only — `urllib.request`, `json`, `re`, `pathlib`.

## Conventions

- Each script writes to a deterministic path relative to repo root.
- No script takes command-line arguments; configuration lives at the top of the file as ALL-CAPS constants.
- Output files are committed alongside source changes; the scripts are documentation of how the artifacts were produced, not a build step that runs on deploy.
- If a script needs to be re-run as part of normal operation, that's noted in `CONTRIBUTING.md` next to the corresponding task.
