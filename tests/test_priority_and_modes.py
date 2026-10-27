"""Tests for priorities, fixed schedules, seasons and hour snoozes."""

from datetime import datetime
from zoneinfo import ZoneInfo

from custom_components.home_maintenance.schedule import (
    due_queue,
    effective_due_date,
    in_season,
    is_due,
    next_fixed_occurrence,
    normalize_months,
    priority_score,
    shift_into_season,
)
from custom_components.home_maintenance.store import HomeMaintenanceTask

TZ = ZoneInfo("Europe/Rome")
NOW = datetime(2026, 10, 28, 10, tzinfo=TZ)


def _task(**extra: object) -> dict:
    return {
        "last_performed": "2026-10-14T00:00:00+02:00",
        "interval_value": 7,
        "interval_type": "days",
        **extra,
    }


def test_fixed_schedule_late_completion_keeps_weekday() -> None:
    monday = datetime(2026, 10, 19, tzinfo=TZ)
    completed_wednesday = datetime(2026, 10, 21, 18, tzinfo=TZ)
    nxt = next_fixed_occurrence(monday, completed_wednesday, 1, "weeks")
    assert nxt.date().isoformat() == "2026-10-26"
    assert nxt.weekday() == 0


def test_fixed_schedule_skips_missed_slots() -> None:
    monday = datetime(2026, 10, 5, tzinfo=TZ)
    completed = datetime(2026, 10, 21, tzinfo=TZ)
    assert next_fixed_occurrence(monday, completed, 1, "weeks").day == 26


def test_fixed_schedule_early_completion_moves_to_next_slot() -> None:
    due = datetime(2026, 10, 26, tzinfo=TZ)
    completed = datetime(2026, 10, 24, tzinfo=TZ)
    assert next_fixed_occurrence(due, completed, 1, "weeks").day == 2


def test_fixed_monthly_does_not_drift_after_short_month() -> None:
    due = datetime(2026, 1, 31, tzinfo=TZ)
    completed = datetime(2026, 3, 5, tzinfo=TZ)
    assert next_fixed_occurrence(due, completed, 1, "months").date().isoformat() == (
        "2026-03-31"
    )


def test_months_are_normalized() -> None:
    assert normalize_months([9, 5, 5, 13, 0]) == [5, 9]
    assert normalize_months(list(range(1, 13))) == []
    assert normalize_months(None) == []


def test_out_of_season_due_moves_to_next_active_month() -> None:
    due = datetime(2026, 10, 18, tzinfo=TZ)
    shifted = shift_into_season(due, [5, 6, 7, 8, 9])
    assert shifted.date().isoformat() == "2027-05-01"


def test_out_of_season_task_is_not_due() -> None:
    task = _task(active_months=[5, 6, 7, 8, 9])
    assert not in_season(task, NOW)
    assert not is_due(task, NOW)
    assert effective_due_date(task).date().isoformat() == "2027-05-01"


def test_hour_snooze_hides_task_until_that_time() -> None:
    task = _task(snoozed_until="2026-10-28T14:00:00+01:00")
    assert not is_due(task, NOW)
    assert is_due(task, datetime(2026, 10, 28, 14, 30, tzinfo=TZ))


def test_priority_score_combines_weight_and_capped_overdue() -> None:
    # Due 2026-10-21, so 7 days overdue on NOW.
    assert priority_score(_task(priority="high"), NOW) == 135
    assert priority_score(_task(), NOW) == 85
    old = _task(priority="low", last_performed="2026-01-01T00:00:00+01:00")
    assert priority_score(old, NOW) == 50
    assert priority_score(_task(priority="bogus"), NOW) == 85


def test_due_queue_orders_by_score_then_duration() -> None:
    tasks = [
        {**_task(), "id": "long", "duration_minutes": 60},
        {**_task(), "id": "short", "duration_minutes": 5},
        {**_task(priority="high"), "id": "high"},
        {**_task(last_performed="2026-10-27T00:00:00+01:00"), "id": "later"},
    ]
    assert [t["id"] for t in due_queue(tasks, NOW)] == ["high", "short", "long"]


def test_new_fields_get_safe_defaults_and_cleaning() -> None:
    task = HomeMaintenanceTask.from_dict(
        {
            "id": "home_maintenance_x",
            "title": "X",
            "interval_value": 1,
            "interval_type": "weeks",
            "last_performed": "2026-10-01T00:00:00+02:00",
            "priority": "urgent",
            "duration_minutes": "-3",
            "schedule_mode": "weird",
            "active_months": [11, 3, 3],
        }
    )
    assert task.priority == "normal"
    assert task.duration_minutes is None
    assert task.schedule_mode == "interval"
    assert task.active_months == [3, 11]
