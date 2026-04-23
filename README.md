# trends-fetcher

Automated log of trending GitHub repositories, deduplicated across runs.

- Source: GitHub Search API (`created:>=<date> stars:>=25`, sorted by stars).
- Updated by `.github/workflows/fetch-trends.yml` every 2 hours.
- Each daily file contains one section per run (UTC time).
- Dedup state lives in `data/seen.json`.
- Proposal output now includes:
  - Genre buckets (including **ゲーム**).
  - Suggested spike branch names per repository (e.g. `spike/<repo>`).
  - A dedicated TypeScript spotlight section.

## Daily logs

- [2026-04-22](trends/2026-04-22.md)

## App proposals

- [2026-04-22](proposals/2026-04-22.md)

## Proposal curation guide

See [docs/proposal-curation.md](docs/proposal-curation.md) for:

- Genre classification rules.
- Branch naming conventions for verification work.
- TypeScript-first review workflow.
