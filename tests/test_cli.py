from __future__ import annotations

import json
from pathlib import Path

import pytest

from trends_fetcher import cli
from trends_fetcher.fetcher import Trend


@pytest.fixture
def fake_trends(monkeypatch: pytest.MonkeyPatch) -> list[Trend]:
    trends = [
        Trend(id=1, title="one", url="https://x/1", score=10, by="a", time=1, descendants=0),
        Trend(id=2, title="two", url=None, score=20, by="b", time=2, descendants=3),
    ]

    def fake_fetch(limit: int = 20, *, client=None) -> list[Trend]:
        return trends[:limit]

    monkeypatch.setattr(cli, "fetch_top_stories", fake_fetch)
    return trends


def test_cli_writes_json_to_stdout(fake_trends, capsys: pytest.CaptureFixture[str]):
    exit_code = cli.main(["--limit", "2"])
    assert exit_code == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert [row["id"] for row in data] == [1, 2]


def test_cli_writes_to_file(fake_trends, tmp_path: Path):
    out = tmp_path / "trends.json"
    cli.main(["--limit", "1", "-o", str(out)])

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data == [
        {
            "id": 1,
            "title": "one",
            "url": "https://x/1",
            "score": 10,
            "by": "a",
            "time": 1,
            "descendants": 0,
        }
    ]


def test_cli_pretty_prints(fake_trends, capsys: pytest.CaptureFixture[str]):
    cli.main(["--limit", "1", "--pretty"])
    captured = capsys.readouterr()
    assert "\n  " in captured.out  # indented output
