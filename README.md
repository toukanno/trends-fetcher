# trends-fetcher

Automated log of trending GitHub repositories, deduplicated across runs.

- Source: GitHub Search API (`created:>=<date> stars:>=25`, sorted by stars).
- Updated by `.github/workflows/fetch-trends.yml` every 2 hours.
- Each daily file contains one section per run (UTC time).
- Dedup state lives in `data/seen.json`.

## Daily logs

- [2026-05-02](trends/2026-05-02.md)
- [2026-05-01](trends/2026-05-01.md)
- [2026-04-30](trends/2026-04-30.md)
- [2026-04-29](trends/2026-04-29.md)
- [2026-04-28](trends/2026-04-28.md)
- [2026-04-27](trends/2026-04-27.md)
- [2026-04-26](trends/2026-04-26.md)
- [2026-04-25](trends/2026-04-25.md)
- [2026-04-24](trends/2026-04-24.md)
- [2026-04-23](trends/2026-04-23.md)
- [2026-04-22](trends/2026-04-22.md)

## App proposals

- [2026-05-02](proposals/2026-05-02.md)
- [2026-04-22](proposals/2026-04-22.md)
