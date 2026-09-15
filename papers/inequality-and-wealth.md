# Wealth concentration: what the measured distribution looks like

Primary-source notes on how unequally the world's wealth and income are
actually distributed, the mechanism economists propose for it, the proposed
remedy, and the contested claim that inequality itself harms social outcomes.

## The measured distribution (World Inequality Report 2026)

**Chancel, L., Piketty, T., Moshrif, R., Zucman, G. et al. (2026). *World
Inequality Report 2026.* World Inequality Lab.** [Executive
summary](https://wir2026.wid.world/insight/executive-summary/) · [global
inequality chapter](https://wir2026.wid.world/insight/global-economic-inequity/).
The report assembles the *Distributional National Accounts* — survey data
reconciled with tax records and national accounts — to estimate the global
distribution. Headline figures:

- The global **top 10% of income-earners earn more than the remaining 90%**;
  the **bottom 50% captures less than 10%** of global income.
- The global **top 10% owns three-quarters of all household wealth**; the
  **bottom 50% owns 2%**.
- The **top 1% alone controls 37%** of global wealth — more than eighteen
  times the wealth of the entire bottom half.
- The **top 0.001%** (about 56,000 adults) own three times more wealth than
  the bottom half of humanity combined; their share rose from almost 4% in
  1995 to over 6% in 2025.

Wealth is roughly an order of magnitude more concentrated than income, because
wealth compounds and is inherited while income is partly tied to current
labour. These are *estimates* built on imperfect data — especially weak in
countries with poor tax-record coverage — but they are the most
methodologically transparent global figures available, with sources and code
published openly via the World Inequality Database.

The previous edition (**WIR 2022**, 2021 data) put the top 10% income share at
52%, the bottom 50% income share at 8.5%, and the top 10% wealth share at 76%.
The direction is unchanged; the 2026 vintage is the one this site now cites.

## The United States, measured (Federal Reserve DFA)

Started from the YouTube video [Wealth Inequality in America (Updated
2026)](https://www.youtube.com/watch?v=2GxlL5-0m_g) (politizane, 8 September
2026), the thirteen-years-later update to the 2012 original. The video is not a
source; every figure below was re-checked against the primary data it draws on.
The cleaned transcript is at
[`../transcripts/2GxlL5-0m_g.en.txt`](../transcripts/2GxlL5-0m_g.en.txt).

**Board of Governors of the Federal Reserve System. *Distributional Financial
Accounts* (DFA), 2026:Q1 release.**
[Interactive chart](https://www.federalreserve.gov/releases/z1/dataviz/dfa/distribute/chart/)
· [full data (zip)](https://www.federalreserve.gov/releases/z1/dataviz/download/zips/dfa.zip).
The DFA distribute the Fed's quarterly household balance sheet (the Z.1
Financial Accounts) across wealth percentiles using the Survey of Consumer
Finances, so the group totals add up to the national aggregate. Figures from
`dfa-networth-shares.csv`, `dfa-networth-levels.csv` and
`dfa-networth-levels-detail.csv`, 2026:Q1:

| Wealth group | Share of net worth | Net worth | Households |
|---|---|---|---|
| Top 0.1% | 14.4% | $25.07T | 136,095 |
| Next 0.9% (rest of top 1%) | 17.2% | $29.96T | 1,212,197 |
| Next 9% (90th–99th) | 36.3% | $63.23T | 12,140,540 |
| Next 40% (50th–90th) | 29.6% | $51.48T | 54,071,475 |
| Bottom 50% | 2.5% | $4.27T | 67,573,814 |
| **All households** | **100%** | **$174.01T** | |

What the video says, and what the data show:

- *"Total wealth of the United States, as of early 2026, $174 trillion."* The
  five groups sum to **$174.01T**. Checks out.
- *"1% of America now has almost a third of all the nation's wealth, roughly
  the same amount the entire bottom 90% has."* Top 1% = 14.4 + 17.2 =
  **31.6%**; bottom 90% = 29.6 + 2.5 = **32.1%**. Checks out.
- *"The bottom 50% only have 2 to 2½%, which is up from 13 years ago."*
  **2.5%** in 2026:Q1, against **0.7–0.9%** in the four quarters of 2013. Checks
  out — the bottom half's share is higher than at its post-2008 trough, though
  still below the **3.5%** of 1989:Q3, when the series begins (the top 1% held
  22.8% then).
- *"The top 1% own half the country's stocks, bonds, and mutual funds. The
  bottom 50% own a measly 1%."* For *corporate equities and mutual fund shares*
  the top 1% hold 24.2 + 26.0 = **50.2%** and the bottom 50% hold **1.1%**.
  Checks out for equities and funds; the DFA put debt securities in a separate
  column, so "bonds" is not part of that 50%.
- *"The average one-percenter has around $40 million"* and *"the 0.1%'s wealth
  is $184 million."* Dividing each group's net worth by its household count:
  $55.03T / 1,348,292 = **$40.8M** per top-1% household; $25.07T / 136,095 =
  **$184.2M** per top-0.1% household. Checks out. Both are per **household**,
  not per person, as the video notes when it says each percentile is "more
  likely 1.3 million households."

**Norton, M.I. & Ariely, D. (2011). "Building a Better America — One Wealth
Quintile at a Time." *Perspectives on Psychological Science* 6(1):9–12.**
[PDF](https://people.duke.edu/~dandan/webfiles/PapersOther/Building%20a%20Better%20America.pdf)
· doi:10.1177/1745691610393524. The study behind the video's opening charts. An
online panel of **5,522** Americans (surveyed December 2005) put the top
quintile's share of wealth at about **59%**, set their ideal at **32%**, and
the actual figure was about **84%**. **92%** preferred an unlabelled pie chart
that was Sweden's distribution over one that was the United States'. Results
held across gender, income, and 2004 vote (Bush voters 90.2%, Kerry voters
93.5%).

**Saez, E. (June 2026). "Striking it Richer: The Evolution of Top Incomes in the
United States (Updated with 2024 estimates)."**
[PDF](https://eml.berkeley.edu/~saez/saez-UStopincomes-2024.pdf). The source
for the video's "Second Gilded Age" chart. The top 1% received **22.4%** of
pre-tax income in 2024, below its 2021 record. Excluding capital gains, the top
10% received **48.3%**.

## The proposed mechanism (Piketty)

**Piketty, T. (2014). *Capital in the Twenty-First Century.* Trans. A.
Goldhammer. Cambridge, MA: Belknap Press of Harvard University Press.** Using
historical tax and wealth series stretching back to the eighteenth century in
France, Britain, the US, and elsewhere, Piketty argues that when the after-tax
**rate of return on capital (r) exceeds the growth rate of the economy (g)**,
inherited and accumulated wealth grows faster than wages and output — so wealth
concentrates over time absent countervailing forces (war, depression,
progressive taxation, rapid growth). The twentieth-century compression of
wealth, on his account, was the *exception* produced by two world wars and
mid-century tax regimes, not a natural equilibrium; the late-twentieth-century
return of high concentration is a regression to the historical pattern.

## The proposed remedy (Zucman, G20 2024)

**Zucman, G. (2024). "A Blueprint for a Coordinated Minimum Effective Taxation
Standard for Ultra-High-Net-Worth Individuals." Commissioned by the Brazilian
G20 presidency. EU Tax Observatory.** The report documents that the world's
roughly **3,000 billionaires pay effective taxes equivalent to about 0.3% of
their wealth** — far below the rate paid by ordinary workers as a share of
income — because much wealth is held as unrealised capital gains and routed
through holding structures. It proposes a coordinated **minimum tax equal to
2% of wealth** for these individuals, estimating it would raise **US$200–250
billion per year**, rising by a further **US$100–140 billion** if extended to
"centimillionaires" (wealth above US$100 million). This is the concrete fiscal
counterpart to the *Abundance* claim that the resources to fund universal
basics already exist.

## The social-outcomes claim (Wilkinson & Pickett)

**Wilkinson, R. & Pickett, K. (2009). *The Spirit Level: Why More Equal
Societies Almost Always Do Better.* London: Allen Lane.** The social
epidemiologists assembled cross-national data for 23 of the richest countries
and the 50 US states, and reported that an index of eleven health and social
problems — life expectancy, infant mortality, mental illness, obesity,
homicide, imprisonment, teenage births, educational scores, social mobility,
trust, and child wellbeing — correlates with *income inequality*, not with
average income, among already-rich societies. Their thesis: above a certain
level of national wealth, the *distribution* of income predicts social
outcomes better than the *level*.

## What needs a caveat

**1. The inequality figures are model-based estimates.** The WIR 2026 numbers
combine surveys, tax data, and national accounts via imputation; coverage and
quality vary sharply across countries, and the very top of the distribution is
the hardest to observe (offshore wealth, private valuations). The direction —
extreme concentration — is robust across methods; the exact percentages carry
real uncertainty and are revised between editions.

**2. Piketty's r > g has been contested.** Critics including Matthew Rognlie
(2015), "Deciphering the Fall and Rise in the Net Capital Share," *Brookings
Papers on Economic Activity*, argue that most of the measured rise in capital's
share is concentrated in *housing*, which behaves differently from the
productive capital Piketty's model emphasises, and that diminishing returns
may limit the r > g divergence. Others dispute the long-run stability of r.
The historical *data series* Piketty assembled are widely used even by his
critics; the contested part is the forecasting model built on them.

**3. The Spirit Level is correlational, and that limit is decisive.** The
relationships are cross-sectional associations, not causal proofs.
Reanalyses — e.g., Snowdon's critique, and academic work such as Avendano
(2012) — argue some associations weaken with different country samples,
outliers (the US drives several panels), or controls, and that reverse
causation and omitted variables (history, ethnic heterogeneity, welfare-state
type) are hard to exclude. Lynch et al. (2004), *Milbank Quarterly* 82(1):5–99,
found the income-inequality/health link inconsistent outside the US. The
honest reading: inequality is *associated* with worse social outcomes in rich
countries; the causal weight of inequality *per se* versus poverty, history,
and institutions remains genuinely debated.

**4. "The money exists" is not the same as "redistribution is costless."** A
2% wealth tax assumes feasible valuation and enforcement against capital
flight; Zucman's design depends on international *coordination* precisely
because uncoordinated wealth taxes have historically been eroded by mobility
and avoidance. The revenue estimate is a ceiling under full compliance.

**5. Parts of the politizane video are not re-verified, and two readings need
care.** The billionaire figures (an average of about $5 billion; more than
$800 billion for the richest person) come from the Forbes list, a media
estimate of private holdings rather than an audited or official series. The
~$13 million floor of the top 1%, the "bottom 8% have zero", and the top-0.01%
average of $971 million trace to DQYDJ's percentile calculator and the World
Inequality Database. The DFA publish none of these, so this page does not rely
on them. Two readings from the video need care. First, Norton & Ariely's 92%
chose between two *unlabelled pie charts*, and Sweden's chart was built from
its *income* distribution (the authors' footnote 2); it was not an endorsement
of a particular ideal curve, and the survey dates from 2005. Second, the
"worst since the 1920s" comparison rests on Saez's *income* shares; the DFA
wealth series starts only in 1989. That 1920s-era inequality *caused* the
Depression is a contested historical claim, not a measurement.

The defensible core for *Abundance*: global wealth is concentrated to a degree
that is well-documented across independent methods; the resources implied by
even a modest coordinated tax on the very top are large relative to the cost of
universal basics; and while the claim that inequality *itself* causes social
harm is contested, the claim that the *means to fund universal provision exist*
does not depend on it.

## Sources

- Chancel, L., Piketty, T., Saez, E. & Zucman, G. (2022). *World Inequality
  Report 2022.* World Inequality Lab. Executive summary:
  <https://wir2022.wid.world/executive-summary/> (full report:
  <https://wir2022.wid.world/>)
- Piketty, T. (2014). *Capital in the Twenty-First Century.* Harvard
  University Press. Publisher record:
  <https://www.hup.harvard.edu/books/9780674430006>
- Zucman, G. (2024). "A Blueprint for a Coordinated Minimum Effective Taxation
  Standard for Ultra-High-Net-Worth Individuals." EU Tax Observatory / G20.
  <https://www.taxobservatory.eu/publication/a-blueprint-for-a-coordinated-minimum-effective-taxation-standard-for-ultra-high-net-worth-individuals/>
  (PDF: <https://gabriel-zucman.eu/files/report-g20.pdf>)
- Wilkinson, R. & Pickett, K. (2009). *The Spirit Level.* Allen Lane / Penguin.
  Publisher record: <https://www.penguin.co.uk/books/56638/the-spirit-level-by-wilkinson-richard/9780241954294>
- Rognlie, M. (2015). "Deciphering the Fall and Rise in the Net Capital
  Share." *Brookings Papers on Economic Activity*, Spring 2015.
  <https://www.brookings.edu/articles/deciphering-the-fall-and-rise-in-the-net-capital-share/>
- Board of Governors of the Federal Reserve System. *Distributional Financial
  Accounts*, 2026:Q1. Chart:
  <https://www.federalreserve.gov/releases/z1/dataviz/dfa/distribute/chart/>
  (data: <https://www.federalreserve.gov/releases/z1/dataviz/download/zips/dfa.zip>)
- Norton, M.I. & Ariely, D. (2011). "Building a Better America — One Wealth
  Quintile at a Time." *Perspectives on Psychological Science* 6(1):9–12.
  doi:10.1177/1745691610393524. PDF:
  <https://people.duke.edu/~dandan/webfiles/PapersOther/Building%20a%20Better%20America.pdf>
- Saez, E. (2026). "Striking it Richer: The Evolution of Top Incomes in the
  United States (Updated with 2024 estimates)." UC Berkeley.
  <https://eml.berkeley.edu/~saez/saez-UStopincomes-2024.pdf>
- Starting point (not a source): politizane (2026). "Wealth Inequality in
  America (Updated 2026)." YouTube. <https://www.youtube.com/watch?v=2GxlL5-0m_g>
  — transcript at [`../transcripts/2GxlL5-0m_g.en.txt`](../transcripts/2GxlL5-0m_g.en.txt)
