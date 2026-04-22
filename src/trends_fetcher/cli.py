"""Command-line entry point for trends-fetcher."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from .fetcher import DEFAULT_LIMIT, fetch_top_stories


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trends-fetcher",
        description="Fetch trending stories from Hacker News.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Number of top stories to fetch (default: {DEFAULT_LIMIT}).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="-",
        help="Output file path, or '-' for stdout (default).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Indent JSON output for readability.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    trends = fetch_top_stories(limit=args.limit)
    payload = [t.to_dict() for t in trends]
    text = json.dumps(payload, indent=2 if args.pretty else None, ensure_ascii=False)

    if args.output == "-":
        sys.stdout.write(text + "\n")
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
