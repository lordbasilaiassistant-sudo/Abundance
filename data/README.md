# `data/` — the numbers behind the page

Every figure displayed on the site is loaded or recomputed from one of these JSON files. **The JSON is canonical. The HTML reflects the JSON.** If they disagree, fix the HTML, never the JSON.

Each file's top-level `$schema` field is a one-line description of what's in it. Each entry inside is a fact with `value`, `unit`, `year`, `source_name`, `source_url`, and a `note` explaining what the number means or what was excluded.

---

## Files

| File | What's in it | Updated by |
|---|---|---|
| [`essentials.json`](essentials.json) | World population, GDP, food kcal supply, freshwater, electricity generation, military spend, etc. ~20 entries, each with primary-source citation. | Hand-edited; re-verify annually. |
| [`pilots.json`](pilots.json) | Six cash-transfer evaluations: GiveDirectly Kenya RCT, Alaska Permanent Fund, Iran 2011, Stockton SEED, Brazil Bolsa Família, Cherokee casino dividend. Each has design + key findings + primary-source URL. | Hand-edited; add new programs as evidence accumulates. |
| [`case-studies.json`](case-studies.json) | Five country-scale precedents for the Omelas pivot: Costa Rica 1948, Norway 1990, Iceland 2008, Bhutan 2008, Mauritius 1968. | Hand-edited. |
| [`countries.json`](countries.json) | Auto-generated — 30 countries × 10 World Bank indicators. Don't hand-edit; re-run `scripts/build_countries.py` instead. | `scripts/build_countries.py` |

---

## Entry schema

Each fact-entry, regardless of file, looks like:

```jsonc
"world_gdp_nominal_usd": {
  "value": 110060000000000,        // raw number, no abbreviation
  "unit": "USD",                   // SI or canonical unit string
  "year": 2024,                    // year of the published figure
  "as_of": "mid-2024",             // optional, for granularity
  "source_name": "IMF World Economic Outlook, April 2026",
  "source_url": "https://...",     // direct primary-source URL
  "note": "Nominal. PPP totals run higher (~$185T)."
}
```

Required fields: `value`, `unit`, `year`, `source_name`, `source_url`.
Optional fields: `as_of`, `note`, any field needed for context.

For pilots and case studies the schema is richer (with `design`, `measurable_outcomes`, etc.) — see those files for the established pattern.

---

## How to add a new entry

1. Find a primary-source URL (institutional publisher, peer-reviewed journal, or government statistical agency).
2. Add an entry following the schema above.
3. Display the number somewhere on the site (typically `index.html` § 2 or § 6).
4. The on-page ratio should be computed in JS from `data/`, not hardcoded.
5. Add the source to `bibliography.md` under the right topic.
6. Open a PR with the citation in the description.

If the entry would replace an existing one (e.g. updated FAO figures), update the value, year, and `source_url` of the existing entry rather than adding a new one.

---

## Why JSON and not a database

- Static files survive forever; databases require maintenance.
- Anyone can read JSON in a text editor; few can run a database.
- GitHub diffs JSON cleanly so changes are auditable in commit history.
- The whole site loads in &lt;100 KB; no need for query optimization.

If the data set grows past what a single JSON file can comfortably hold, split by topic (one file per essential). Don't introduce a database.
