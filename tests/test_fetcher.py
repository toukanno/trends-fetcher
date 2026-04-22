from __future__ import annotations

from typing import Any

import pytest

from trends_fetcher.fetcher import TOP_STORIES_URL, Trend, fetch_top_stories


class FakeResponse:
    def __init__(self, payload: Any) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> Any:
        return self._payload


class FakeClient:
    def __init__(self, responses: dict[str, Any]) -> None:
        self._responses = responses
        self.requested: list[str] = []

    def get(self, url: str) -> FakeResponse:
        self.requested.append(url)
        if url not in self._responses:
            raise AssertionError(f"unexpected URL requested: {url}")
        return FakeResponse(self._responses[url])


def _item(item_id: int, **overrides: Any) -> dict[str, Any]:
    base = {
        "id": item_id,
        "title": f"story {item_id}",
        "url": f"https://example.com/{item_id}",
        "score": 10 * item_id,
        "by": f"user{item_id}",
        "time": 1_700_000_000 + item_id,
        "descendants": item_id,
    }
    base.update(overrides)
    return base


def _client_with(ids: list[int], items: dict[int, dict[str, Any]]) -> FakeClient:
    responses: dict[str, Any] = {TOP_STORIES_URL: ids}
    for item_id, item in items.items():
        responses[f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"] = item
    return FakeClient(responses)


def test_fetch_top_stories_respects_limit():
    client = _client_with([1, 2, 3, 4, 5], {1: _item(1), 2: _item(2)})
    trends = fetch_top_stories(limit=2, client=client)

    assert [t.id for t in trends] == [1, 2]
    assert all(isinstance(t, Trend) for t in trends)
    assert client.requested[0] == TOP_STORIES_URL
    assert len(client.requested) == 3  # top + 2 items


def test_fetch_top_stories_zero_limit_returns_empty():
    client = _client_with([1, 2], {})
    assert fetch_top_stories(limit=0, client=client) == []
    assert client.requested == []


def test_fetch_top_stories_handles_missing_optional_fields():
    client = _client_with(
        [42],
        {42: {"id": 42, "title": "only title"}},
    )
    [trend] = fetch_top_stories(limit=1, client=client)

    assert trend.id == 42
    assert trend.title == "only title"
    assert trend.url is None
    assert trend.score == 0
    assert trend.descendants == 0


def test_fetch_top_stories_skips_null_items():
    client = _client_with([1, 2], {1: None, 2: _item(2)})  # type: ignore[dict-item]
    trends = fetch_top_stories(limit=2, client=client)

    assert [t.id for t in trends] == [2]


def test_trend_to_dict_round_trips():
    trend = Trend(id=1, title="t", url=None, score=5, by="u", time=0, descendants=0)
    assert trend.to_dict() == {
        "id": 1,
        "title": "t",
        "url": None,
        "score": 5,
        "by": "u",
        "time": 0,
        "descendants": 0,
    }


def test_fetch_top_stories_stops_at_available_ids():
    client = _client_with([7], {7: _item(7)})
    trends = fetch_top_stories(limit=50, client=client)
    assert len(trends) == 1


def test_negative_limit_returns_empty():
    client = _client_with([1], {})
    assert fetch_top_stories(limit=-3, client=client) == []


@pytest.mark.parametrize("limit", [1, 3, 5])
def test_fetch_top_stories_various_limits(limit: int):
    ids = list(range(1, 6))
    items = {i: _item(i) for i in ids}
    trends = fetch_top_stories(limit=limit, client=_client_with(ids, items))
    assert [t.id for t in trends] == ids[:limit]
