# `papers/` — deep notes on specific scholarly works

This folder holds longer-form notes on individual papers, books, or studies that are load-bearing for the site's arguments. Each note records the source, the key claims that are used on the site, and — importantly — the published critiques of the source, so future contributors and readers can judge the evidence themselves.

The shorter, list-form bibliography lives at the project root as [`bibliography.md`](../bibliography.md). This folder is for deeper engagement with specific works.

## Current notes

| File | What it covers |
|---|---|
| [`historical-context.md`](historical-context.md) | Anthropological and historical sources supporting § 8 of the main page: Lee on Ju/'hoansi work hours, Wiessner on firelight talk, Ekirch + Wehr on segmented sleep, Conard on the Hohle Fels flute, Larsen on bioarchaeology of agriculture. Includes the substantial revision to Lee's numbers and the Sahlins / Suzman debate. |

## How to add a paper note

Use this when:

- A single source is load-bearing for a specific claim on the page (i.e. removing the source would weaken the argument).
- The source has well-documented critiques or caveats that the page should acknowledge.
- The source is long enough that a one-line bibliography entry doesn't do it justice.

Don't use this for:

- General-interest references (those go in `bibliography.md`).
- Primary-source data (those go in `data/`).
- Raw transcripts (those go in `transcripts/`).

### Template

```markdown
# Paper title

Author(s), Year. *Journal* / *Publisher*. URL.

## What's load-bearing
- Claim 1 (used in § X of `index.html`)
- Claim 2 (used in `bibliography.md` / `case-studies.html` / ...)

## Primary source
- DOI / direct link
- Open-access version if any

## What checks out
[Direct quote + page reference for each load-bearing claim, with paraphrased context.]

## What needs a caveat
[Known critiques, contradictory findings, limitations the author acknowledges.]

## Related works
- See also: ...
```
