# trends-fetcher

Automated log of trending GitHub repositories, deduplicated across runs.

- Source: GitHub Search API (`created:>=<date> stars:>=25`, sorted by stars).
- Updated by `.github/workflows/fetch-trends.yml` every 2 hours.
- Each daily file contains one section per run (UTC time).
- Dedup state lives in `data/seen.json`.

## Daily logs

- [2026-04-22](trends/2026-04-22.md)
