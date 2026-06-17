# Abundance

**A primary-sourced arithmetic of what humanity already produces — divided by how many of us there are.**

Live site: **https://lordbasilaiassistant-sudo.github.io/Abundance/**

This project is one thing: a sanity check, with citations.

For each essential resource that has reliable global production data — food,
water, electricity, output (GDP) — it divides the world total by the UN's
mid-2024 population estimate and compares the result to a published minimum
need. Every number links to its primary source (FAO, IEA, IMF, WHO, World Bank,
UN-Habitat, SIPRI, UBS). If a claim has no link, it is not in the repo.

## The thesis

In 2026, the world produces enough food, water, electricity, and output to meet
every human's basic needs. Hunger, homelessness, and energy poverty are
**distribution outcomes**, not **production outcomes**. And the standard
objection — "if you give people money, they'll stop working / waste it / it
isn't sustainable" — fails in every well-designed pilot we have on record
(Kenya RCT, Alaska 1982-present, Iran 2011, Stockton SEED).

This is a factual claim, not a political program. The page makes that claim,
shows the arithmetic, cites the empirical pilots, and includes an interactive
calculator so readers can stress-test their own redistribution scenarios. It
does not argue that money can be abolished, that universal rollout is
politically feasible, or that transition is costless. See
[`methodology.md`](methodology.md) for the limits.

The page also names what Le Guin called the *Omelas* bargain — the implicit
claim that some people's suffering is the price of others' comfort — and asks
the empirical question: is the suffering load-bearing? The evidence base says no.

## What's in here

- **[The main page](index.html)** — the per-capita arithmetic for ~14 essentials, recomputed in JS from cited data.
- **[An open letter](letter.html)** — the case made to anyone who can act on this, without attack; cited throughout. Also in [Español](lang/es/letter.html), [Français](lang/fr/letter.html), [Português](lang/pt/letter.html), [العربية](lang/ar/letter.html), [中文](lang/zh/letter.html), and [हिन्दी](lang/hi/letter.html).
- **[Country case studies](case-studies.html)** — eleven nations that chose to lift underclass suffering, each with its honest counter-narrative.
- **[By country](countries.html)** — a sortable drill-down of 91 countries × 10 World Bank indicators.
- **[Free tools](tools/)** — an image editor, image compressor, QR code generator, color contrast checker, and password generator that run entirely in your browser: no account, no upload, no tracking. The "manufactured scarcity" argument, demonstrated in code.
- **[Deep notes](papers/)** and a **[~100-entry bibliography](bibliography.md)** — including a standing steelman of the [strongest case *against* this project](papers/counterarguments.md).

## What this is *not*

- Not a manifesto. The tone is arithmetic, not advocacy.
- Not a hand-wave. Every per-capita figure on the page is recomputed in JS at
  load time from the raw numbers in [`data/essentials.json`](data/essentials.json).
  If the script disagrees with the page, the page is wrong.
- Not viral content. No emojis, no "shocking truths," no AI-generated imagery.
- Not tracking you. No analytics, no cookies, no third-party scripts.

## Structure

The project is intentionally vanilla — static HTML/CSS/JS plus JSON. No framework, no build step. You can edit a file in the GitHub web UI and the deploy happens automatically.

```
Abundance/
├── index.html              # main page (commented sections)
├── letter.html             # open letter to whoever can act — the moral close
├── countries.html          # per-country drill-down
├── case-studies.html       # country-scale precedents
├── tools/                  # free, client-side tools (manufactured-scarcity demos)
│   ├── image-editor/       # in-browser image editor — no upload, no account
│   ├── image-compressor/   # batch compress/resize/convert — no upload
│   ├── qr/                 # QR code generator (full ISO/IEC 18004 encoder)
│   ├── contrast/           # WCAG 2.1 color contrast checker
│   └── password/           # offline password generator (cryptographic RNG)
├── style.css               # imports styles/*.css — don't edit directly
│
├── styles/                 # MODULAR CSS — edit here
│   ├── tokens.css          # colors, fonts, sizes
│   ├── base.css            # resets, typography, links, headings
│   ├── layout.css          # container, masthead, sections, hero, TOC, footer
│   ├── components.css      # cards, pilots, stats, dials, FAQ
│   └── print.css           # print/PDF override
│
├── data/                   # every number on the site lives here
│   ├── README.md           # schemas + how to add an entry
│   ├── essentials.json     # food / water / electricity / GDP / etc.
│   ├── pilots.json         # 12 cash-transfer evaluations
│   ├── case-studies.json   # 11 country precedents
│   └── countries.json      # 91 countries × 10 World Bank indicators
│
├── embed/calculator.html   # standalone iframe-able calculator
├── lang/es/index.html      # Spanish; pattern for other languages
│
├── papers/                 # deep notes on specific scholarly works
├── scripts/                # regeneration utilities (Python)
├── transcripts/            # raw research material (auto-VTT downloads)
│
├── bibliography.md         # ~100 academic references organized by topic
├── methodology.md          # how each number was derived + honest limits
├── CONTRIBUTING.md         # full contributor guide ← start here
├── CITATION.cff            # how to cite the project
└── README.md
```

For "where do I add X?" see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full guide. The single rule:

> **Primary sources or it didn't happen.** Wikipedia, news articles, advocacy orgs, AI chatbots, "as everyone knows" — none of these qualify.

Quick standards:
1. **Primary source required.** Peer-reviewed journal, government statistical agency, or institutional publication.
2. **Year of publication required.** Stale numbers get retired.
3. **Unit and methodology required.** "Global energy" is meaningless without knowing if it's primary energy, final energy, or just electricity.
4. **No projections, only published figures.** If a number is modeled, say so.

## Translations

The data is universal; the language barrier isn't. Current state:

| Language | Status | Path |
|---|---|---|
| English | full (canonical) | [`/`](index.html) |
| Español | summary version | [`/lang/es/`](lang/es/index.html) |
| 中文 (Mandarin) | not started | help wanted |
| हिन्दी (Hindi) | not started | help wanted |
| العربية (Arabic) | not started | help wanted (RTL) |
| Français | not started | help wanted |
| Português | not started | help wanted |

**How to contribute a translation:**
1. Fork the repo.
2. Copy `lang/es/index.html` as `lang/{your-code}/index.html`.
3. Translate the prose. Leave the numbers, source URLs, and `<code>` blocks alone — those are language-independent.
4. Add `<link rel="alternate" hreflang="{your-code}" href="...">` to both your new file and the main `index.html`.
5. Add a `<url>` block to `sitemap.xml` for your file, with the appropriate `<xhtml:link rel="alternate" hreflang>` entries on the root `<url>`.
6. Add yourself to the eyebrow language switcher on the main `index.html`.
7. Open a pull request. You will be credited in `CITATION.cff` as a translator.

Machine translation is acceptable if labeled clearly. Native-speaker review is preferred. Either is better than English-only.

## License

Public domain — [CC0 1.0](LICENSE). Take it, fork it, ship it, embed it,
disprove it. Knowledge about whether humanity can feed itself should not be
property.
