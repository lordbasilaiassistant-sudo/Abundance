# `transcripts/` — raw research material

Transcripts of source material (YouTube videos, talks, lectures) used while researching the site. Kept in the repo for transparency: if a section of `index.html` was informed by a video, that video's transcript is here so anyone can verify the claim wasn't fabricated from context.

The transcripts themselves are **not** primary sources. They are the unstructured material from which we extracted claims, each of which was then re-verified against an actual primary source before going on the page.

## Files

| File | Source | Used by |
|---|---|---|
| `TQd2k1pEXp4.en.vtt` / `TQd2k1pEXp4.en.txt` | YouTube — *"What Did Ancient Humans Do All Day Before Jobs Existed?"* (Axen, May 2026) | § 8 of `index.html`. Anthropological claims sourced from this video were re-verified against Lee (1968), Wiessner (2014), Ekirch (2024), Conard (2009), Larsen (1995). See [`../papers/historical-context.md`](../papers/historical-context.md). |

## How to add a transcript

If a video, podcast, or talk informs a section of the site:

1. Use `yt-dlp` (for YouTube) to download the `.vtt` auto-captions:
   ```
   py -m yt_dlp --skip-download --write-auto-sub --sub-lang en --sub-format vtt \
                --output "transcripts/%(id)s.%(ext)s" "<URL>"
   ```
2. Clean the VTT into plain text:
   ```
   py scripts/clean_vtt.py transcripts/{id}.en.vtt
   ```
3. Verify every load-bearing claim in the transcript against an actual primary source before adding it to the site.
4. Document the verification in `papers/{topic}.md`.

## Why keep these?

For exactly the reason this whole project exists: claims should be auditable. A reader who wants to know "where did this number come from?" can follow:

> `index.html` → cited primary source → `bibliography.md` → optionally `papers/{topic}.md` → optionally `transcripts/{id}.txt`

…all in this repo, in plain text, forever.
