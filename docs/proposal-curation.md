# Proposal curation guide

This repository generates app proposals from trending GitHub projects.

## Genre buckets

The proposal generator classifies repositories by lightweight keyword matching:

- ゲーム
- AI/エージェント
- 開発者ツール
- データ/分析
- インフラ/バックエンド
- その他

The **ゲーム** bucket is designed to surface game-related opportunities quickly.

## Branch naming for validation

Each proposal includes a suggested validation branch:

- `spike/<repo-name>`

Use these branches for short experiments before deciding whether to merge learnings
into production branches.

## TypeScript review track

TypeScript repositories are listed again in a dedicated section:

- `TypeScript注目枠`

This is useful when prioritizing frontend/full-stack exploration and SDK-style
tooling opportunities.
