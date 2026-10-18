#!/usr/bin/env python3
"""
Fetch public GitHub contribution calendar data for a user and write a JSON snapshot.

This mirrors the data-collection stage used in profile-art pipelines like
AVIVASHISHTA29/AVIVASHISHTA29, but keeps the data model explicit and testable.
"""

from __future__ import annotations

import json
import pathlib
import sys
from datetime import date, datetime, timedelta
from typing import Any

import bs4
import requests

USER = "developer-mohanaditya"
OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"
OUT_PATH = OUT_DIR / "contributions.json"
CONTRIBUTIONS_URL = f"https://github.com/users/{USER}/contributions"


def parse_calendar(soup: bs4.BeautifulSoup) -> list[dict[str, Any]]:
    rows = []
    cells = soup.select("td.ContributionCalendar-day")
    for td in cells:
        date_str = td.get("data-date")
        if not date_str:
            continue
        try:
            day_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        count_text = td.get("title") or ""
        count = 0
        for token in count_text.split():
            if token.isdigit():
                count = int(token)
                break
        level = int(td.get("data-level") or 0)
        rows.append(
            {
                "date": date_str,
                "count": count,
                "level": level,
            }
        )
    return rows


def summarize(days: list[dict[str, Any]]) -> dict[str, Any]:
    by_date = {d["date"]: d["count"] for d in days}
    active_days = sum(1 for c in by_date.values() if c > 0)
    total = sum(by_date.values())
    average = round(total / active_days, 2) if active_days else 0.0

    sorted_dates = sorted(by_date.keys())
    current_streak = 0
    longest_streak = 0
    streak = 0
    yesterday = None

    for d in sorted_dates:
        if by_date[d] > 0:
            if yesterday is None or (date.fromisoformat(d) - date.fromisoformat(yesterday)).days == 1:
                streak += 1
            else:
                streak = 1
            if streak > longest_streak:
                longest_streak = streak
            yesterday = d
        else:
            streak = 0

    current_streak = longest_streak
    if sorted_dates:
        last_active = sorted_dates[-1]
        if by_date.get(last_active, 0) > 0:
            current_streak = 1
            cursor = date.fromisoformat(last_active)
            while True:
                cursor = cursor + timedelta(days=1)
                if by_date.get(cursor.isoformat(), 0) > 0:
                    current_streak += 1
                else:
                    break

    best_day = max(by_date.values()) if by_date else 0
    monthly: dict[str, int] = {}
    for d, c in by_date.items():
        key = d[:7]
        monthly[key] = monthly.get(key, 0) + c

    return {
        "user": USER,
        "updated_at": datetime.utcnow().date().isoformat(),
        "active_days": active_days,
        "total": total,
        "average_per_active_day": average,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly": dict(sorted(monthly.items())),
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    headers = {"User-Agent": "profile-readme-bot/1.0"}
    try:
        resp = requests.get(CONTRIBUTIONS_URL, headers=headers, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"Failed to fetch contributions: {exc}", file=sys.stderr)
        return 2

    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    days = parse_calendar(soup)

    if not days:
        print("No contribution cells found; the page markup may have changed.", file=sys.stderr)
        return 1

    summary = summarize(days)
    payload = {
        "summary": summary,
        "days": days,
    }

    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH} with {len(days)} days and summary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
