# Contributing to Abundance

Thank you for choosing abundance over scarcity. This file describes how to add to the project. The single overarching rule:

> **Primary sources or it didn't happen.** Wikipedia, news articles, advocacy organizations, AI chatbots, and "as everyone knows" do not qualify as primary sources. The page exists because every number on it traces to a peer-reviewed study or an authoritative institutional publication, and any contribution that breaks that property weakens the whole project.

If you're not sure whether a source counts, open a draft PR and ask. Better to argue about evidence quality on the public record than to ship a soft citation.

---

## Where to add what

The project is intentionally vanilla — static HTML/CSS/JS plus JSON data files. No framework, no build step, no Node dependencies. You can edit a file in the GitHub web UI and the deploy will happen automatically.

| You want to… | Edit / add |
|---|---|
| Add a new essential (alongside food / water / electricity / GDP) | New entry in `data/essentials.json` + new `.card` block in `index.html` § 2 |
| Add a new cash-transfer pilot | New entry in `data/pilots.json` + new `.pilot` block in `index.html` § 6 |
| Add a new country case study | New entry in `data/case-studies.json` + new section in `case-studies.html` |
| Add or update a country in the drill-down | Edit the `COUNTRIES` list in `scripts/build_countries.py`, re-run, commit the regenerated `data/countries.json` |
| Add a new FAQ answer | New `<details class="card">` in `index.html` § 10 *and* a matching entry in the JSON-LD `FAQPage` schema in the `<head>` |
| Add a new translation | Copy `lang/es/index.html` to `lang/{your-code}/index.html`. Translate prose; keep numbers, code blocks, and source URLs unchanged. Add `hreflang` to both pages and to `sitemap.xml`. Add yourself to `CITATION.cff`. See the [Translations table in `README.md`](README.md#translations). |
| Add an academic reference | Add it to `bibliography.md` under the right topic. If a paper is load-bearing for a specific claim, also cite it inline in the relevant section. |
| Add a new visual style | Edit the right file under `styles/` (see below) — don't touch `style.css` directly. |
| Fix a number that has been superseded by a newer publication | Update the value in the right `data/*.json`, update the inline display in `index.html`, update the citation year, and note the change in the PR description. |

---

## Project structure

```
Abundance/
├── README.md, LICENSE, CITATION.cff, CONTRIBUTING.md
├── methodology.md            # how each number was derived
├── bibliography.md           # ~100 academic references by topic
├── robots.txt, sitemap.xml   # crawler hints
├── favicon.png, apple-touch-icon.png, og.png   # branding (regen via scripts/)
│
├── index.html                # main page (commented section markers, single file by intent)
├── countries.html            # per-country drill-down
├── case-studies.html         # 11 country precedents
├── style.css                 # imports from styles/ (do not edit directly)
│
├── styles/                   # ← edit CSS here
│   ├── tokens.css            # colors, fonts, sizes
│   ├── base.css              # resets, typography, links, headings
│   ├── layout.css            # container, masthead, sections, hero, TOC, footer
│   ├── components.css        # cards, pilots, stats, dials, FAQ
│   └── print.css             # print/PDF override
│
├── data/                     # ← every number on the site lives here
│   ├── README.md             # schemas + how to add an entry
│   ├── essentials.json       # food / water / electricity / GDP / etc.
│   ├── pilots.json           # 12 cash-transfer evaluations
│   ├── case-studies.json     # 11 precedents (Costa Rica … Uruguay)
│   └── countries.json        # 91 countries × 10 World Bank indicators
│
├── embed/
│   ├── calculator.html       # standalone iframe-able calculator
│   └── README.md             # embed snippet + sizing notes
│
├── lang/
│   └── es/index.html         # Spanish summary; pattern for other languages
│
├── papers/                   # ← deep notes on specific scholarly works
│   ├── README.md
│   └── historical-context.md # Lee, Wiessner, Ekirch, Conard, Larsen
│
├── scripts/                  # ← regeneration scripts (Python 3, stdlib + Pillow)
│   ├── README.md
│   ├── build_countries.py    # fetches countries.json from World Bank API
│   ├── clean_vtt.py          # cleans YouTube auto-VTT into plain text
│   ├── make_og.py            # generates og.png from data
│   └── make_favicon.py       # generates favicon.png + apple-touch-icon.png
│
├── transcripts/              # ← raw research material, not on the public site
│   ├── README.md
│   └── TQd2k1pEXp4.*         # transcript backing § 8 (historical context)
│
└── .github/workflows/pages.yml
```

---

## Commit conventions

- **One change per PR.** Adding a pilot is one PR. Updating GDP is another.
- **Cite every change.** Commit messages and PR descriptions should link the primary source supporting the number.
- **Re-run the right script.** If you edit something a script generates (e.g. countries.json, og.png), regenerate it; don't hand-edit.
- **Don't break the math.** Every ratio displayed on the page is recomputed in JS from the raw values in `data/`. If the script disagrees with the page, the page is wrong — and that means the JSON, the inline display, and any schema citation in `index.html` `<head>` all need to update together.
- **No CSS in HTML.** All styles in `styles/`. Exception: `embed/calculator.html` inlines its CSS on purpose so it works as a one-file embed.

---

## Visual / design standards

- **No emoji.** Anywhere.
- **No four-sided card borders.** Either no border, a single-side accent rail, or a tinted background.
- **No "shocking truth" framing.** The page is arithmetic, not advocacy.
- **No AI-generated text without primary-source backing.** If you can't link a source, don't write the claim.
- **Bigger numbers than prose.** When a ratio is on the page, it should dominate the surrounding text.
- **One color for abundance (green), one for unevenness (amber), one for shortfall (red).** Don't add new accent colors without changing `styles/tokens.css`.

---

## Translation contributions

See the **Translations** section in [`README.md`](README.md#translations). Six languages are stubbed in the README as "help wanted." Machine translation with a clear "machine-translated" banner is acceptable. Native-speaker review is preferred.

---

## Disagreement is welcome

The page is in the public domain (CC0). It exists to be argued with on the public record. If you think a claim is wrong, open an issue. If you can replace it with a better-cited claim, open a PR. The bibliography section ["What needs a caveat"](papers/historical-context.md#what-needs-a-caveat) is a model — we include the counter-evidence inline.

The unacceptable contribution: making the page less honest in order to make the argument easier. Stronger evidence for the thesis is welcome. Weaker evidence for the thesis is not — and a weaker thesis with stronger evidence is welcomer still.

---

## Conduct

Be useful. Be specific. Argue with the data, not with the people. We don't have a separate `CODE_OF_CONDUCT.md` because the GitHub-default works fine.
