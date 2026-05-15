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
**distribution outcomes**, not **production outcomes**.

This is a factual claim, not a political program. The page makes that claim
and shows the arithmetic. It does not argue that money can be abolished, that
UBI is politically feasible, or that redistribution is costless. See
[`methodology.md`](methodology.md) for the limits.

## What this is *not*

- Not a manifesto. The tone is arithmetic, not advocacy.
- Not a hand-wave. Every per-capita figure on the page is recomputed in JS at
  load time from the raw numbers in [`data/essentials.json`](data/essentials.json).
  If the script disagrees with the page, the page is wrong.
- Not viral content. No emojis, no "shocking truths," no AI-generated imagery.
- Not tracking you. No analytics, no cookies, no third-party scripts.

## Structure

| File | What it is |
|---|---|
| [`index.html`](index.html) | The site itself — one page, no framework. |
| [`style.css`](style.css) | Dark, sober typography. No JS animations. |
| [`data/essentials.json`](data/essentials.json) | Every raw number, with source URL, year, and note. |
| [`methodology.md`](methodology.md) | What was included, excluded, and known limits. |
| [`refs/historical-context.md`](refs/historical-context.md) | Source notes for the anthropological / historical section (Lee, Wiessner, Ekirch, Conard, Larsen). |
| [`.github/workflows/pages.yml`](.github/workflows/pages.yml) | Auto-deploys to GitHub Pages on push to `main`. |

## Contributing

This page exists to be corrected. If you find a number that conflicts with
its cited source, that has been superseded, or that lacks a primary-source
citation, please open an issue or PR.

Standards for additions:
1. **Primary source or no source.** Wikipedia, news articles, advocacy orgs,
   and AI chatbots do not count.
2. **Year of publication required.** Stale numbers get retired.
3. **Unit and methodology required.** "Global energy" is meaningless without
   knowing if it's primary energy, final energy, or just electricity.
4. **No projections, only published figures.** If a number is modeled, say so.

## License

Public domain — [CC0 1.0](LICENSE). Take it, fork it, ship it, embed it,
disprove it. Knowledge about whether humanity can feed itself should not be
property.
