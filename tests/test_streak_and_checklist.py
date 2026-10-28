"""Tests for weekly streaks and checklist normalization."""

from datetime import datetime
from zoneinfo import ZoneInfo

from custom_components.home_maintenance.store import (
    HomeMaintenanceTask,
    normalize_checklist,
    normalize_done,
)
from custom_components.home_maintenance.streak import (
    compute_streak,
    task_occurrences,
    week_start,
)

TZ = ZoneInfo("Europe/Rome")
# Wednesday 28 October 2026; the current week starts Monday 26 October.
NOW = datetime(2026, 10, 28, 10, tzinfo=TZ)


def _weekly(history: list[str], **extra: object) -> dict:
    return {
        "priority": "high",
        "interval_value": 1,
        "interval_type": "weeks",
        "last_performed": f"{history[-1]}T00:00:00+01:00",
        "history": [f"{d}T00:00:00+01:00" for d in history],
        **extra,
    }


def test_week_start_is_monday() -> None:
    assert week_start(NOW.date()).isoformat() == "2026-10-26"


def test_occurrences_rebuilt_from_history() -> None:
    occ = task_occurrences(_weekly(["2026-10-05", "2026-10-12"]), NOW)
    assert [(o.due.isoformat(), o.done and o.done.isoformat()) for o in occ] == [
        ("2026-10-12", "2026-10-12"),
        ("2026-10-19", None),
    ]


def test_streak_counts_weeks_without_overdue_high_tasks() -> None:
    task = _weekly(["2026-09-28", "2026-10-05", "2026-10-12", "2026-10-19"])
    streak = compute_streak([task], NOW)
    # Weeks of Sep 28, Oct 5, Oct 12, Oct 19 are all clean.
    assert streak.current == 4
    assert streak.best == 4
    # The occurrence due Oct 26 is still open today.
    assert streak.current_week_ok is False


def test_late_completion_breaks_the_streak_until_done() -> None:
    # Due Oct 5, done only on Oct 14: weeks of Oct 5 ends overdue.
    task = _weekly(["2026-09-21", "2026-09-28", "2026-10-14", "2026-10-21"])
    streak = compute_streak([task], NOW)
    assert streak.current == 2  # weeks of Oct 12 and Oct 19
    assert streak.best == 2
    assert streak.recent_weeks == (True, True, False, True, True)


def test_skipped_occurrence_keeps_the_week() -> None:
    task = _weekly(
        ["2026-09-28", "2026-10-12", "2026-10-19"],
        skipped=["2026-10-05T00:00:00+02:00"],
    )
    # The occurrence due Oct 5 was skipped, so the Oct 12 completion answers
    # the occurrence due Oct 12 and no week is left overdue.
    streak = compute_streak([task], NOW)
    assert streak.current == 4
    assert streak.best == 4


def test_only_tracked_priority_counts() -> None:
    low = _weekly(["2026-09-07", "2026-10-21"], priority="low")
    assert compute_streak([low], NOW).tracked_tasks == 0
    assert compute_streak([low], NOW).current == 0


def test_no_history_means_no_streak() -> None:
    task = {
        "priority": "high",
        "interval_value": 1,
        "interval_type": "weeks",
        "last_performed": "2026-10-25T00:00:00+02:00",
        "history": [],
    }
    streak = compute_streak([task], NOW)
    assert streak.current == 0
    assert streak.weeks_tracked == 0
    assert streak.current_week_ok is True


def test_checklist_normalization() -> None:
    assert normalize_checklist(" Sanitari \n\nSpecchio\n Pavimento ") == [
        "Sanitari",
        "Specchio",
        "Pavimento",
    ]
    assert normalize_checklist(["a", " ", None, "b"]) == ["a", "b"]
    assert normalize_checklist(42) == []
    assert normalize_done([2, "1", 1, 9, -1, "x"], 3) == [1, 2]


def test_task_from_dict_cleans_checklist() -> None:
    task = HomeMaintenanceTask.from_dict(
        {
            "id": "home_maintenance_bath",
            "title": "Bagno",
            "interval_value": 1,
            "interval_type": "weeks",
            "last_performed": "2026-10-19T00:00:00+02:00",
            "checklist": ["Sanitari", "Specchio"],
            "checklist_done": [0, 5],
        }
    )
    assert task.checklist == ["Sanitari", "Specchio"]
    assert task.checklist_done == [0]
    assert task.checklist_autocomplete is True
