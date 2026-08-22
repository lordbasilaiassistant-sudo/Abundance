# Methodology

This document records, for every figure on the site, what was included, what
was excluded, where averages mask distribution, and which numbers we judged
*not* honest enough to publish.

## Divisor

We use **8.2 billion** — the UN World Population Prospects 2024 mid-year
estimate. Source: [WPP 2024 Summary of Results (PDF)](https://population.un.org/wpp/assets/Files/WPP2024_Summary-of-Results.pdf).

This is rounded to the nearest 100 million. Mid-2024 estimate is 8.16B; mid-2025
projection is ~8.23B. We chose 8.2B as the working divisor and note the rounding
introduces <1% error in any per-capita figure.

## Per-essential notes

### Food

- **Numerator:** `3,006 kcal / person / day` — the global average dietary energy
  supply, per the [FAO Food Balance Sheets 2010–2023](https://www.fao.org/statistics/highlights-archive/highlights-detail/food-balance-sheets-2010-2023/en)
  (FAOSTAT release of 28 October 2025). In 2023 the world crossed the historic
  milestone of 3,000 kcal/person/day for the first time (exact world value:
  3,005.6, retrievable from [FAOSTAT](https://www.fao.org/faostat/en/#data/FBS)
  and mirrored by [Our World in Data](https://ourworldindata.org/food-supply)).
  This number is the dietary energy available *for human consumption* after
  accounting for animal feed, seed, industrial use, and post-harvest loss.
- **Denominator (need):** `2,100 kcal / person / day` — the conventional
  FAO/WHO/UNU reference for an average adult ([Human Energy Requirements,
  2001](https://www.fao.org/4/y5686e/y5686e00.htm)). Actual requirements
  vary by age, sex, body mass, and activity. We use it because it is the most
  commonly cited reference floor in food-security literature.
- **What this ratio misses:** calories aren't nutrition. A population can be
  calorically adequate and micronutrient-deficient. The site does not address
  protein, vitamin, or mineral sufficiency.

### Water

- **Numerator:** `43,000 km³ / year` of renewable freshwater, per FAO AQUASTAT.
- **Denominator (need):** `50 L / person / day` — the WHO "intermediate access"
  level for drinking, cooking, and basic hygiene ([WHO 2003 guideline](https://www.who.int/publications/i/item/WHO-SDE-WSH-03.02)).
  Survival minimum is 7.5 L/day; full health protection is ~100 L/day.
- **What this ratio misses:** the biggest limitation on this page. Renewable
  freshwater is geographically locked. The Amazon basin discharges more water
  than the Sahara, Sahel, and Arabian Peninsula combined. Per-capita global
  averages tell you the global total is abundant; they do not tell you the
  water is where the people are. Transport, desalination, and storage are real
  costs that the ratio ignores. The "287×" figure is honest about aggregate
  supply and dishonest if read as "local supply."

### Electricity

- **Numerator:** `32,202 TWh / year` — reported 2025 global generation, per the
  [Energy Institute Statistical Review of World Energy 2026](https://www.energyinst.org/statistical-review),
  up 857 TWh (3%) on 2024. This replaces the prior derived estimate (IEA 2023
  generation plus a reported growth increment) with a single published total.
  Ember's [Global Electricity Review 2026](https://ember-energy.org/latest-insights/global-electricity-review-2026/)
  independently reports 2025 demand growth of 849 TWh and renewables at a record
  33.8% of generation, overtaking coal for the first time in over a century.
- **Denominator (need):** two thresholds, because the IEA's "Tier 1" definition
  (100 kWh/person/year) is widely considered too low to enable economic
  development. The Modern Energy Minimum (1,000 kWh/person/year) includes
  productive uses such as small machines, refrigeration, and commercial
  lighting.
- **What this ratio misses:** electricity is not all energy. The world used
  ~635 EJ of primary energy in 2024; only a fraction reaches end users as
  electricity. The site focuses on electricity because the access framework
  exists there and because electrification of heat and transport is the
  forward trajectory.

### Output (GDP)

- **Numerator:** `$118.18 trillion` — the 2025 world aggregate in the IMF World
  Economic Outlook, April 2026 vintage ($118,175.485 billion; 2024 was
  $111,598.554B). Nominal, current prices. PPP-adjusted world GDP runs
  considerably higher; we use nominal because the comparison to the World Bank
  poverty line is also in current USD.
- **Denominator (need):** `$3.00 / day × 365 = $1,095 / year` — the World Bank's
  updated International Poverty Line ([June 2025 update](https://www.worldbank.org/en/news/factsheet/2025/06/05/june-2025-update-to-global-poverty-lines)),
  which replaced the prior $2.15/day (2017 PPP) line.
- **What this ratio misses:** GDP is not income. It includes capital
  consumption, government spending, and net exports. A claim that "GDP per
  capita is 13× the poverty line" is not a claim that everyone's *income* is
  13× the line — only that the world's output, if it flowed directly to
  households, would average that much per person.

### Housing

- **Numerator missing on purpose.** There is no clean global number for
  "housing units built per year." We considered using rooms-per-person from UN
  Demographic Yearbooks and rejected it as too noisy.
- **Distribution evidence (instead):** 318M homeless and 2.8B in inadequate
  housing globally, per UN-Habitat and UN DESA. In wealthy countries, vacant
  units consistently exceed homeless counts by an order of magnitude or more.
  Sources cited inline on the page.

## UBI math, fully shown

Universal $3/day floor for every human alive:

```
$3.00 × 8,200,000,000 people × 365 days = $8,979,000,000,000
                                        ≈ $8.98 trillion / year
                                        ≈ 7.6% of world GDP ($118.18T)
```

Closing the **poverty gap** (paying only the difference between current income
and $3/day, for the 847M people below the line) costs much less, because most
poor people are not at zero income. The World Bank's poverty-gap statistic
indicates the average shortfall is roughly $1/day per affected person, putting
the closure cost well under $1 trillion / year — comparable to a single year's
*increase* in global military spending.

We did not put the gap number on the page because we could not find a single
2024-vintage published gap figure we trust enough. If we find one, we will add
it with citation.

## What is deliberately left out

- **"What if we abolished money."** This is a political and philosophical
  question, not an arithmetic one. The page restricts itself to arithmetic.
- **GDP critiques.** GDP is a flawed measure — it counts oil spills and divorce
  lawyers as growth. But it is the measure the IMF publishes. Using it does
  not endorse it.
- **Wealth confiscation.** The site notes that $213.8T is held by 58M people
  to make a factual point about distribution. It does not claim that wealth
  should be — or could be — directly redistributed, which is a separate
  question with separate technical answers.
- **National-level data.** Per-country breakdowns are important but out of
  scope for v1. They exist in every cited source if you want to drill in.

## Errors and updates

If a number on the site disagrees with this document, or either disagrees with
its cited source, **the source wins**. Open an issue or PR on the GitHub repo
and the page will be corrected.
