# Backlog

A standing, ordered list of improvements to this repository. The daily
maintenance Routine reads this file, picks **one** item, ships it as a draft
pull request, and moves the item to Done with the PR number. New ideas get
appended as candidates rather than implemented on the spot — one improvement
per pass, so every change stays reviewable.

Ordering is by value to the project's single purpose: *every claim traceable to
a primary source, readable by anyone, in any language, without a build step.*
Rewrite the order freely; do not silently skip the top item without saying why.

**Sizing:** `S` = one sitting, one file or two. `M` = a focused session.
`L` = needs a human decision before starting — propose, don't build.

---

## Next up

1. **`S` Archive every primary source to the Wayback Machine, and record the snapshot.**
   Two citations rotted in the first automated check of this repo. The fix that
   scales is not vigilance, it is archival: submit each `*_source_url` to
   `web.archive.org/save/`, store the resulting snapshot URL as `archived_url`
   alongside it, and render it as a small "archived copy" link next to each
   citation. Then a 404 degrades to an inconvenience instead of an unsourced
   number. Start with `data/essentials.json` (36 entries); extend to
   `pilots.json` and `case-studies.json` in later passes.

2. **`S` Cross-check `bibliography.md` against the data files.**
   The bibliography has ~112 entries; the data files carry their own
   `primary_source_name` / `primary_source_url` pairs. Nothing keeps them
   agreeing. Add a check to `scripts/check.py`: every `primary_source_url` in
   `data/pilots.json` and `data/case-studies.json` should appear somewhere in
   `bibliography.md`, and report the ones that don't. Fix the gaps it finds.

3. **`S` Serve `papers/` and `transcripts/` as real URLs.**
   README links `papers/` as a directory. That resolves on GitHub, but GitHub
   Pages returns 404 — there is no `index.html`. Add a small index page for
   `papers/` listing each note with its one-line summary (and decide whether
   `transcripts/` should be indexed or stay unlisted research material). Add to
   `sitemap.xml` and `llms.txt`; `scripts/check.py` will hold it in sync.

4. **`M` JSON Schema for the data files.**
   `data/README.md` describes the schemas in prose and `check.py` enforces a
   thin version (source URL present, year present). Write real JSON Schema
   documents under `data/schema/`, validate against them in `check.py` with a
   stdlib validator, and let the schema — not the prose — be the contract a
   contributor or an agent reads.

5. **`M` JSON-LD on the pages that lack it.**
   `index.html`, `essay.html` and `datacenter-water.html` carry structured
   data; `letter.html`, `course.html`, `countries.html` and `case-studies.html`
   do not. This site exists to be cited, and `robots.txt` invites the AI
   crawlers explicitly — machine-readable authorship, dates and citations on
   every page directly serve that. Use `Article` / `Dataset` as appropriate and
   keep the claims identical to the visible page.

6. **`M` Run the tools pages through the repo's own contrast checker.**
   `tools/contrast/` implements WCAG 2.1 contrast. Audit every page in the site
   against it (including `styles/tokens.css` pairings and the RTL Arabic
   letter), record the results in a short `docs/` note or an issue, and fix the
   failures. Dogfooding an accessibility tool the project ships is worth more
   than a badge.

7. **`M` Port the main page into a second language.**
   README calls this the highest-value contribution: the open letter exists in
   all seven languages, the arithmetic page in two. Order by reach: Hindi,
   Mandarin, Arabic, French, Portuguese. Translate prose only — numbers, source
   URLs and `<code>` blocks are language-independent. Label machine translation
   clearly as the README requires, and add `hreflang` both ways, `sitemap.xml`,
   `llms.txt`, the README table and `CITATION.cff`.

8. **`M` A data-provenance changelog.**
   The README "Data currency" table shows the current vintage but not its
   history. A `CHANGELOG-data.md` recording each figure change — old value, new
   value, publication that superseded it, date — turns "trust us, it's current"
   into something a skeptic can audit. Backfill from git history.

9. **`L` Decide whether `countries.html` should degrade without JavaScript.**
   The homepage deliberately works without JS; the country drill-down fetches
   `data/countries.json` and renders client-side, so it shows nothing. Options:
   a static snapshot of the top N countries in the HTML, a generated static
   table, or an explicit "requires JavaScript, here is the raw JSON" fallback.
   Each trades bytes against reach. **Propose, get a decision, then build.**

10. **`L` An `abundance.json` machine endpoint.**
    `llms.txt` indexes the site for agents; there is no single endpoint that
    returns every headline figure with its source, unit, year and per-capita
    result. The Graveyard already publishes `graves.json` in this spirit. Needs
    a decision on shape and stability guarantees before anyone builds it.

## Candidate ideas (not yet ordered — append here)

- Per-figure permalinks (`essay.html#food`) so a citation can point at one number.
- A "what would change my mind" section per claim, paired with the counterarguments paper.
- Automated `lastmod` updates in `sitemap.xml` from git commit dates.
- Check that every figure rendered in HTML matches the JSON it claims to come from (the strongest possible version of the "if the script disagrees with the page, the page is wrong" rule).
- Print/PDF pass: verify `styles/print.css` produces a readable letter and essay.

## Done

- Repo map, `llms.txt`, self-check, citation-rot checker, two dead citations repointed — [#6](https://github.com/lordbasilaiassistant-sudo/Abundance/pull/6).
