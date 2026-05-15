# Abundance calculator — embeddable

The redistribution calculator from the Abundance project, packaged for embedding on any third-party site.

**Live preview:** https://lordbasilaiassistant-sudo.github.io/Abundance/embed/calculator.html

## How to embed

Paste this anywhere in your HTML:

```html
<iframe src="https://lordbasilaiassistant-sudo.github.io/Abundance/embed/calculator.html"
        width="100%" height="720"
        style="border:1px solid #262932; border-radius:6px; max-width:760px"
        loading="lazy"
        title="Abundance calculator — universal income floor vs redistribution math"></iframe>
```

That's the whole installation.

## What it does

A reader moves four sliders — income floor ($/day), wealth tax above $1M, military spending redirect, food-waste recovery — and the widget recomputes:

- Annual cost of a universal income floor for every human alive
- That cost as a share of world GDP
- Revenue from the redistribution dials chosen
- Calories recovered from waste reduction
- Net funding gap, with a verdict that adapts

All inputs are real published figures:

- **Population:** UN World Population Prospects 2024 (8.2B mid-2024)
- **World GDP:** IMF World Economic Outlook April 2026 ($110.06T)
- **Wealth above $1M:** UBS Global Wealth Report 2024 ($213.8T held by 58M people)
- **Global military spending:** SIPRI 2024 ($2.7T)
- **Food waste/loss:** FAO + UNEP Food Waste Index 2024 (32% of global production)

## Sizing

Recommended height ranges:

| Container width | Recommended `height` |
|---|---|
| ≥ 760px | 720 |
| 480–760px | 780 |
| ≤ 480px (mobile) | 900 |

The widget is responsive; the height accommodates the four-dial layout collapsing to one column on narrow viewports.

## License

Public domain (CC0). Embed without attribution if you want — but a link back to the [main Abundance page](https://lordbasilaiassistant-sudo.github.io/Abundance/) is appreciated, since that's where the full citations and limits live.

## Customizing

The widget is a single self-contained HTML file at `calculator.html`. Fork the repo, change values in the `D` object at the bottom of the file, and host wherever you like. Updating the underlying numbers to your own jurisdiction's data (national GDP, national wealth, national military spend) takes about ten seconds.
