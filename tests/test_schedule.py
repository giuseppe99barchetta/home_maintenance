"""Tests for scheduling helpers."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from custom_components.home_maintenance.schedule import (
    calculate_next_due,
    day_delta,
    effective_due_date,
    task_status,
)

TZ = ZoneInfo("Europe/Rome")


def test_month_end_clamps_cleanly() -> None:
    value = datetime(2026, 1, 31, tzinfo=TZ)
    assert calculate_next_due(value, 1, "months").date().isoformat() == "2026-02-28"


def test_leap_year_yearly_schedule() -> None:
    value = datetime(2024, 2, 29, tzinfo=TZ)
    assert calculate_next_due(value, 1, "years").date().isoformat() == "2025-02-28"


def test_year_interval_supported() -> None:
    value = datetime(2026, 8, 27, tzinfo=TZ)
    assert calculate_next_due(value, 2, "years").year == 2028


def test_unknown_interval_rejected() -> None:
    with pytest.raises(ValueError):
        calculate_next_due(datetime(2026, 1, 1, tzinfo=TZ), 1, "fortnights")


def test_snooze_wins_over_regular_due_date() -> None:
    task = {
        "last_performed": "2026-08-01T00:00:00+02:00",
        "interval_value": 7,
        "interval_type": "days",
        "snoozed_until": "2026-09-01T00:00:00+02:00",
    }
    assert effective_due_date(task).date().isoformat() == "2026-09-01"


def test_skip_override_is_used() -> None:
    task = {
        "last_performed": "2026-08-01T00:00:00+02:00",
        "interval_value": 7,
        "interval_type": "days",
        "next_due_override": "2026-09-10T00:00:00+02:00",
    }
    assert effective_due_date(task).date().isoformat() == "2026-09-10"


def test_calendar_day_delta_is_dst_safe() -> None:
    due = datetime(2026, 3, 30, tzinfo=TZ)
    now = datetime(2026, 3, 29, 23, 30, tzinfo=TZ)
    assert day_delta(due, now) == 1


def test_task_statuses() -> None:
    now = datetime(2026, 8, 27, 12, tzinfo=TZ)
    base = {
        "last_performed": "2026-08-20T00:00:00+02:00",
        "interval_type": "days",
    }
    assert task_status({**base, "interval_value": 6}, now) == "overdue"
    assert task_status({**base, "interval_value": 7}, now) == "due_today"
    assert task_status({**base, "interval_value": 10}, now) == "due_soon"
    assert task_status({**base, "interval_value": 30}, now) == "later"
