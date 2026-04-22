#!/usr/bin/env python3
"""Fetch trending GitHub repositories and append a deduplicated Markdown log.

Strategy: the GitHub REST API does not expose github.com/trending directly,
so we approximate it by querying repositories created within the recent window
and ranking them by stars. Repos that have already been written to a previous
daily file are skipped via ``data/seen.json``.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRENDS_DIR = ROOT / "trends"
DATA_DIR = ROOT / "data"
SEEN_FILE = DATA_DIR / "seen.json"
README = ROOT / "README.md"

WINDOW_DAYS = 7
MIN_STARS = 25
PER_PAGE = 50
MAX_PAGES = 4
LANGUAGES: tuple[str | None, ...] = (None,)  # None = all languages


def _request(url: str, token: str | None) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "trends-fetcher",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def search_repos(since: str, language: str | None, token: str | None) -> list[dict]:
    q_parts = [f"created:>={since}", f"stars:>={MIN_STARS}"]
    if language:
        q_parts.append(f"language:{language}")
    query = " ".join(q_parts)

    items: list[dict] = []
    for page in range(1, MAX_PAGES + 1):
        url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
            {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": PER_PAGE,
                "page": page,
            }
        )
        try:
            data = _request(url, token)
        except urllib.error.HTTPError as exc:
            print(f"search failed on page {page}: {exc}", file=sys.stderr)
            break
        batch = data.get("items", [])
        items.extend(batch)
        if len(batch) < PER_PAGE:
            break
    return items


def load_seen() -> set[str]:
    if not SEEN_FILE.exists():
        return set()
    try:
        return set(json.loads(SEEN_FILE.read_text()))
    except json.JSONDecodeError:
        return set()


def save_seen(seen: set[str]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(json.dumps(sorted(seen), indent=2) + "\n")


def format_row(item: dict) -> str:
    name = item["full_name"]
    url = item["html_url"]
    stars = item.get("stargazers_count", 0)
    lang = item.get("language") or "—"
    desc = (item.get("description") or "").replace("\n", " ").replace("|", "\\|").strip()
    if not desc:
        desc = "_(no description)_"
    return f"| [{name}]({url}) | {stars:,} | {lang} | {desc} |"


def append_run_section(now: datetime, since: str, new_items: list[dict]) -> Path:
    TRENDS_DIR.mkdir(parents=True, exist_ok=True)
    today = now.date().isoformat()
    path = TRENDS_DIR / f"{today}.md"

    lines: list[str] = []
    if not path.exists():
        lines.append(f"# Trending repositories — {today}")
        lines.append("")
        lines.append(
            "New repositories (created within the last "
            f"{WINDOW_DAYS} days, ``stars >= {MIN_STARS}``) discovered on this "
            "date. Each section corresponds to one scheduled run; repositories "
            "already seen in prior runs are filtered out."
        )
        lines.append("")

    time_label = now.strftime("%H:%M UTC")
    lines.append(f"## {time_label} — {len(new_items)} new")
    lines.append("")
    lines.append(f"_Search window: created on or after `{since}`._")
    lines.append("")
    lines.append("| Repository | Stars | Language | Description |")
    lines.append("| --- | ---: | --- | --- |")
    for item in new_items:
        lines.append(format_row(item))
    lines.append("")

    with path.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return path


def rebuild_index() -> None:
    files = sorted(TRENDS_DIR.glob("*.md"), reverse=True)
    lines = [
        "# trends-fetcher",
        "",
        "Automated log of trending GitHub repositories, deduplicated across runs.",
        "",
        "- Source: GitHub Search API (`created:>=<date> stars:>=25`, sorted by stars).",
        "- Updated by `.github/workflows/fetch-trends.yml` every 2 hours.",
        "- Each daily file contains one section per run (UTC time).",
        "- Dedup state lives in `data/seen.json`.",
        "",
        "## Daily logs",
        "",
    ]
    if not files:
        lines.append("_No runs yet._")
    else:
        for f in files:
            lines.append(f"- [{f.stem}](trends/{f.name})")
    lines.append("")
    README.write_text("\n".join(lines))


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN")
    now = datetime.now(timezone.utc)
    since = (now.date() - timedelta(days=WINDOW_DAYS)).isoformat()

    all_items: dict[str, dict] = {}
    for language in LANGUAGES:
        for item in search_repos(since, language, token):
            all_items.setdefault(item["full_name"], item)

    seen = load_seen()
    new_items = [it for it in all_items.values() if it["full_name"] not in seen]
    new_items.sort(key=lambda it: it.get("stargazers_count", 0), reverse=True)

    if not new_items:
        print("No new trending repositories since last run.")
        rebuild_index()
        return 0

    path = append_run_section(now, since, new_items)
    seen.update(it["full_name"] for it in new_items)
    save_seen(seen)
    rebuild_index()
    print(f"Appended {len(new_items)} new repos to {path.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
