# trends-fetcher

A small CLI that fetches the current top stories from [Hacker News](https://news.ycombinator.com/)
via the public Firebase API and emits them as JSON.

## Requirements

- Python 3.11+

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
# 20 stories to stdout
trends-fetcher

# 5 stories, pretty-printed, written to a file
trends-fetcher --limit 5 --pretty -o trends.json

# Or run as a module
python -m trends_fetcher --limit 10
```

Each story is serialized as:

```json
{
  "id": 12345,
  "title": "...",
  "url": "https://...",
  "score": 42,
  "by": "username",
  "time": 1700000000,
  "descendants": 7
}
```

## Development

```bash
pytest             # run the tests
ruff check .       # lint
ruff format .      # format
```
