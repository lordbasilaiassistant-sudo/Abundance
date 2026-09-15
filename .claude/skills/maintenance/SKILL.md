---
name: maintenance
description: Routine upkeep pass on the Abundance repo — run the self-check, hunt citation rot, verify data vintages against the published sources, and open a draft PR with whatever needs fixing. Use for scheduled maintenance, "check the repo", "is anything stale", or before a release.
---

# Abundance maintenance pass

Read [`AGENTS.md`](../../../AGENTS.md) first — repo map, invariants, task recipes.
Everything below assumes those invariants, especially: **primary sources or it
didn't happen**, numbers live in `data/*.json`, published URLs never move, and
generated files are regenerated rather than hand-edited.

Work through the steps in order. Most passes find nothing; that is a success,
and it should end quietly rather than with a PR full of churn.

## 1. Structural check (always)

```bash
python3 scripts/check.py
```

Fix anything it reports. It covers citations-present, internal links, sitemap,
`llms.txt`, page metadata, and documentation drift (undocumented scripts,
orphan stylesheets, a README data vintage that disagrees with the data).

## 2. Citation rot (always)

```bash
python3 scripts/check_sources.py --md
```

- **DEAD (404/410)** — the cited document is gone, so the number it backs is
  currently unsourced. Find its new home (publisher DOI, the institution's
  repository, e.g. WHO IRIS, or the Wayback Machine), **open it and confirm it
  is the same document with the same figure**, then update every place the URL
  appears: `data/*.json`, the page HTML, `bibliography.md`, `methodology.md`.
  Repointing a moved document is maintenance. Swapping in a *different* source
  because the original vanished is a data change — say so explicitly in the PR
  and do not do it silently.
- **INCONCLUSIVE (403/429/redirect)** — publishers block scripts routinely.
  Do not touch these. Mention them in the PR only if the same URL has been
  inconclusive for several passes.

## 3. Data vintages (weekly-ish, or when a publisher's release month arrives)

The README "Data currency" table lists each headline figure and its vintage.
For any figure whose publisher has since released a newer edition (FAO SOFI,
SIPRI April, IMF WEO April/October, UBS GWR, Tracking SDG7, WHO GHED, ITU):

1. Read the new publication and take the figure from it directly — never from
   coverage of it.
2. Update `data/*.json` (value, `year`, `source_name`, `source_url`), the
   inline display in the page, and the README table together.
3. If methodology changed between editions, say so in the entry `note` and in
   the PR. The repo already carries one such caveat (UBS GWR 2024 → 2026);
   match that honesty.
4. Do not update a figure you could not verify against the primary document.

## 4. Report

- Nothing to change → say so, and stop. No empty PR, no busywork commit.
- Something to change → one branch, one focused PR, **draft**, with:
  - what changed and why, linking each primary source;
  - the `scripts/check.py` output;
  - anything you found but deliberately did not change, and what a human needs
    to decide.
- Never merge, approve, or force-push. The maintainer decides what ships.
