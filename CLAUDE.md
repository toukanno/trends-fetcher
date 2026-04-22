# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

`trends-fetcher` is a small Python CLI that fetches the current top stories from
Hacker News (via the public Firebase API at `https://hacker-news.firebaseio.com/v0`)
and emits them as JSON to stdout or a file. There is no database, no scheduler, and
no auth — one invocation = one HTTP fan-out + one JSON write.

## Commands

Bootstrap (one-time):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Day-to-day:

```bash
pytest                                   # run all tests
pytest tests/test_fetcher.py             # single file
pytest tests/test_fetcher.py::test_fetch_top_stories_respects_limit  # single test
pytest -k limit                          # by keyword

ruff check .                             # lint
ruff format .                            # format
ruff check --fix .                       # auto-fix lint

trends-fetcher --limit 5 --pretty        # run the CLI
python -m trends_fetcher --limit 5       # equivalent module form
```

## Architecture

`src/` layout with one package, `trends_fetcher`:

- `fetcher.py` — owns the HN API contract. `fetch_top_stories(limit, *, client=None)`
  is the single public entry point. It calls `/topstories.json` to get an ID list,
  then `/item/{id}.json` per story, and returns a list of frozen `Trend` dataclasses.
  The `client` kwarg takes any object with a `get(url) -> response` method
  (`response.raise_for_status()` and `response.json()`), which is how tests inject
  fakes without patching. If `client` is `None`, a short-lived `httpx.Client` is
  created and closed inside the call.
- `cli.py` — argparse wrapper. `main(argv=None) -> int` is the console-script
  target declared in `pyproject.toml` (`trends-fetcher = "trends_fetcher.cli:main"`).
  It calls `fetch_top_stories`, serializes via `Trend.to_dict`, and writes to
  stdout or `-o <path>`.
- `__main__.py` — enables `python -m trends_fetcher`.

The important boundary: `fetcher.py` is the only module that knows HN URLs or
response shapes. `cli.py` only speaks in `Trend` objects. When adding a new data
source, prefer adding a sibling fetcher module (e.g. `fetcher_github.py`) that
returns the same `Trend` shape rather than growing `fetcher.py`.

## Conventions worth knowing

- **Testing HTTP without the network.** Tests never hit the real API and never
  monkeypatch `httpx`. They build a `FakeClient` (see `tests/test_fetcher.py`)
  that records requested URLs and returns canned payloads, and pass it in via
  the `client=` kwarg. Follow that pattern for any new fetcher; do not add
  `responses`/`httpx.MockTransport` unless there's a concrete reason.
- **`Trend` is frozen.** Treat it as an immutable value object. If you need to
  transform one, build a new instance.
- **Missing fields are expected.** HN items regularly lack `url`, `descendants`,
  etc. `_trend_from_item` defaults them; keep that behavior when extending the
  dataclass rather than raising on missing keys.
- **`fetch_top_stories` owns the client lifecycle.** If it creates the client,
  it closes it in `finally`. If the caller passes one in, the caller owns it.
  Preserve this invariant.
- **Ruff config** (in `pyproject.toml`) enables `E, F, I, UP, B, SIM` and
  targets py311. Run `ruff format` before committing; CI will be strict once added.
