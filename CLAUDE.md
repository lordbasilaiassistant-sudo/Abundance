# CLAUDE.md

See [`AGENTS.md`](AGENTS.md) — the canonical repository map, invariants, and task recipes for this project.

Short version: static site, no build step, every number lives in `data/*.json` with a primary-source URL, published URLs are stable (do not move files), and `python3 scripts/check.py` is the test suite — run it before every PR.
