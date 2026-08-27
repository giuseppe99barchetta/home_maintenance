"""Scheduling helpers for Home Maintenance tasks."""

from __future__ import annotations

from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

INTERVAL_TYPES = ("days", "weeks", "months", "years")


def calculate_next_due(
    last_performed: datetime, interval_value: int, interval_type: str
) -> datetime:
    """Calculate the next due date for a recurring task."""
    if interval_type == "days":
        return last_performed + timedelta(days=interval_value)
    if interval_type == "weeks":
        return last_performed + timedelta(weeks=interval_value)
    if interval_type == "months":
        return last_performed + relativedelta(months=interval_value)
    if interval_type == "years":
        return last_performed + relativedelta(years=interval_value)
    raise ValueError(f"Unsupported interval type: {interval_type}")


def effective_due_date(task: dict, now: datetime | None = None) -> datetime | None:
    """Return the task's effective due date after skip/snooze overrides."""
    del now
    override = task.get("next_due_override")
    if override:
        try:
            due = datetime.fromisoformat(override)
        except (TypeError, ValueError):
            return None
    else:
        try:
            last = datetime.fromisoformat(task["last_performed"])
            due = calculate_next_due(
                last,
                int(task["interval_value"]),
                str(task["interval_type"]),
            )
        except (KeyError, TypeError, ValueError):
            return None

    snoozed_until = task.get("snoozed_until")
    if snoozed_until:
        try:
            snoozed = datetime.fromisoformat(snoozed_until)
        except (TypeError, ValueError):
            snoozed = None
        if snoozed is not None and snoozed > due:
            due = snoozed

    return due.replace(hour=0, minute=0, second=0, microsecond=0)


def day_delta(due: datetime, now: datetime) -> int:
    """Return whole calendar-day difference between due and now."""
    return (due.date() - now.date()).days


def task_status(task: dict, now: datetime) -> str:
    """Return a stable UI-friendly task status."""
    due = effective_due_date(task, now)
    if due is None:
        return "unknown"
    delta = day_delta(due, now)
    if delta < 0:
        return "overdue"
    if delta == 0:
        return "due_today"
    if delta <= 7:
        return "due_soon"
    return "later"
