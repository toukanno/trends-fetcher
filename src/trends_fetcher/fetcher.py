"""Fetch top stories from the Hacker News Firebase API."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Protocol

import httpx

HN_BASE_URL = "https://hacker-news.firebaseio.com/v0"
TOP_STORIES_URL = f"{HN_BASE_URL}/topstories.json"
ITEM_URL_TEMPLATE = f"{HN_BASE_URL}/item/{{item_id}}.json"

DEFAULT_TIMEOUT = 10.0
DEFAULT_LIMIT = 20


@dataclass(frozen=True)
class Trend:
    id: int
    title: str
    url: str | None
    score: int
    by: str
    time: int
    descendants: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class _HTTPClient(Protocol):
    def get(self, url: str) -> Any: ...


def _get_json(client: _HTTPClient, url: str) -> Any:
    response = client.get(url)
    response.raise_for_status()
    return response.json()


def _trend_from_item(item: dict[str, Any]) -> Trend:
    return Trend(
        id=int(item["id"]),
        title=item.get("title", ""),
        url=item.get("url"),
        score=int(item.get("score", 0)),
        by=item.get("by", ""),
        time=int(item.get("time", 0)),
        descendants=int(item.get("descendants", 0)),
    )


def fetch_top_stories(
    limit: int = DEFAULT_LIMIT,
    *,
    client: _HTTPClient | None = None,
) -> list[Trend]:
    """Fetch the top N stories from Hacker News.

    Pass ``client`` to inject a preconfigured httpx.Client (or a test double).
    """
    if limit <= 0:
        return []

    owns_client = client is None
    http: _HTTPClient = client or httpx.Client(timeout=DEFAULT_TIMEOUT)
    try:
        top_ids: list[int] = _get_json(http, TOP_STORIES_URL)
        trends: list[Trend] = []
        for item_id in top_ids[:limit]:
            item = _get_json(http, ITEM_URL_TEMPLATE.format(item_id=item_id))
            if item is None:
                continue
            trends.append(_trend_from_item(item))
        return trends
    finally:
        if owns_client and hasattr(http, "close"):
            http.close()
