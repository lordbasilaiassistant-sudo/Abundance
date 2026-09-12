# `tools/` — client-side utilities

Five free tools that run entirely in the browser: no account, no upload, no
server, no tracking. They are the "manufactured scarcity" argument demonstrated
in code — each replaces a product that is commonly sold, gated, or ad-supported.

| Path | Tool | Notes |
|---|---|---|
| [`index.html`](index.html) | Tool index | The landing page that links the five tools. |
| [`image-editor/`](image-editor/index.html) | In-browser image editor | Canvas-based; the file never leaves the machine. |
| [`image-compressor/`](image-compressor/index.html) | Batch compress / resize / convert | Multiple files at once, still local-only. |
| [`qr/`](qr/index.html) | QR code generator | Full ISO/IEC 18004 encoder implemented in the page. |
| [`contrast/`](contrast/index.html) | WCAG 2.1 contrast checker | Used to check this site's own palette. |
| [`password/`](password/index.html) | Password generator | Uses `crypto.getRandomValues`, never `Math.random`. |

## Conventions

- **One file per tool.** Each `index.html` is self-contained: markup, styles and
  logic in the same file. There is no bundler and no shared runtime.
- **No third-party JavaScript.** No CDN scripts, no analytics, no fonts fetched
  per tool. If a tool needs an algorithm, the algorithm is implemented here.
- **Nothing leaves the browser.** No `fetch` to a backend, no uploads, no
  telemetry. This is the product claim; don't weaken it for convenience.
- **Directory URLs are public.** `tools/qr/` etc. are cited externally — don't
  rename or move a tool directory.
- Adding a tool: create `tools/{name}/index.html`, link it from `index.html`,
  add it to `sitemap.xml` and `llms.txt`, then run `python3 scripts/check.py`.
