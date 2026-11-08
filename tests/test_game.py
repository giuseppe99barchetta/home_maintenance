"""Tests for points, challenges and recaps."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from custom_components.home_maintenance.game import (
    period_range,
    recap_message,
    standings,
    winners,
)
from custom_components.home_maintenance.store import HomeMaintenanceTask

TZ = ZoneInfo("Europe/Rome")
# Wednesday 28 October 2026.
NOW = datetime(2026, 10, 28, 10, tzinfo=TZ)


def _weekly(history: list[str], by: list[str | None], priority: str) -> dict:
    return {
        "priority": priority,
        "interval_value": 1,
        "interval_type": "weeks",
        "last_performed": f"{history[-1]}T00:00:00+01:00",
        "history": [f"{d}T00:00:00+01:00" for d in history],
        "history_by": by,
    }


def test_period_ranges() -> None:
    assert period_range("week", NOW.date()) == (date(2026, 10, 26), date(2026, 11, 1))
    assert period_range("week", NOW.date(), previous=True) == (
        date(2026, 10, 19),
        date(2026, 10, 25),
    )
    assert period_range("month", NOW.date(), previous=True) == (
        date(2026, 9, 1),
        date(2026, 9, 30),
    )


def test_points_on_time_bonus_and_unattributed() -> None:
    # Due Oct 12 done on time by Anna; due Oct 19 done late (Oct 21) by Luca.
    high = _weekly(
        ["2026-10-05", "2026-10-12", "2026-10-21"],
        [None, "person.anna", "Luca"],
        "high",
    )
    low = _weekly(["2026-10-13"], ["Luca"], "low")
    rows = standings([high, low], NOW, date(2026, 10, 1), date(2026, 10, 31))
    luca = {"who": "Luca", "points": 5, "completions": 2, "on_time": 1, "high": 1}
    anna = {"who": "person.anna", "points": 4, "completions": 1, "on_time": 1}
    assert rows == [luca, {**anna, "high": 1}]
    assert winners(rows) == {
        "champion": ["Luca"],
        "punctual": ["Luca", "person.anna"],
        "firefighter": ["Luca", "person.anna"],
    }


def test_done_together_credits_everyone() -> None:
    low = _weekly(["2026-10-13"], ["person.anna,Luca"], "low")
    rows = standings([low], NOW, date(2026, 10, 1), date(2026, 10, 31))
    assert [(r["who"], r["points"]) for r in rows] == [("Luca", 2), ("person.anna", 2)]


def test_nobody_wins_an_empty_period() -> None:
    assert winners([]) == {"champion": [], "punctual": [], "firefighter": []}
    recap = {
        "period": "week",
        "start": "2026-10-19",
        "end": "2026-10-25",
        "standings": [],
        "winners": {},
    }
    assert "Nessuno" in recap_message(recap, "it")


def test_history_by_is_aligned_with_history() -> None:
    task = HomeMaintenanceTask.from_dict(
        {
            "id": "t",
            "title": "T",
            "interval_value": 1,
            "interval_type": "weeks",
            "last_performed": "2026-10-12T00:00:00+01:00",
            "history": ["2026-10-05T00:00:00+01:00", "2026-10-12T00:00:00+01:00"],
        }
    )
    assert task.history_by == [None, None]
