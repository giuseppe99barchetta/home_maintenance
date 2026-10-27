"""Scheduling helpers for Home Maintenance tasks."""

from __future__ import annotations

from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

INTERVAL_TYPES = ("days", "weeks", "months", "years")
DUE_SOON_DAYS = 7

PRIORITIES = ("low", "normal", "high")
DEFAULT_PRIORITY = "normal"
PRIORITY_WEIGHTS = {"high": 100, "normal": 50, "low": 0}
OVERDUE_POINTS_PER_DAY = 5
OVERDUE_POINTS_MAX_DAYS = 10

SCHEDULE_MODES = ("interval", "fixed")
DEFAULT_SCHEDULE_MODE = "interval"

_MAX_FIXED_STEPS = 5000


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
    msg = f"Unsupported interval type: {interval_type}"
    raise ValueError(msg)


def next_fixed_occurrence(
    due: datetime,
    completed: datetime,
    interval_value: int,
    interval_type: str,
) -> datetime:
    """
    Return the next anchored occurrence after a completion.

    Fixed schedules keep the original rhythm: the next due date is the first
    multiple of the interval after the current due date that falls after the
    completion day. Completing early (or on time) moves to the next slot;
    completing late skips the slots that were missed instead of drifting.
    Multiples are computed from the anchor so month-end clamping never drifts.
    """
    for step in range(1, _MAX_FIXED_STEPS + 1):
        candidate = calculate_next_due(due, interval_value * step, interval_type)
        if candidate.date() > completed.date():
            return candidate
    msg = "Could not find the next fixed occurrence."
    raise ValueError(msg)


def normalize_months(months: list[int] | None) -> list[int]:
    """Return a sorted, de-duplicated list of valid month numbers."""
    if not months:
        return []
    clean = sorted({int(m) for m in months if 1 <= int(m) <= 12})  # noqa: PLR2004
    return [] if len(clean) == 12 else clean  # noqa: PLR2004


def shift_into_season(due: datetime, active_months: list[int] | None) -> datetime:
    """Move a due date to the first day of the next active month if needed."""
    months = normalize_months(active_months)
    if not months or due.month in months:
        return due
    shifted = due.replace(day=1)
    for _ in range(12):
        shifted += relativedelta(months=1)
        if shifted.month in months:
            return shifted
    return due


def in_season(task: dict, now: datetime) -> bool:
    """Return True when the current month is one of the task's active months."""
    months = normalize_months(task.get("active_months"))
    return not months or now.month in months


def _parse(value: str | None) -> datetime | None:
    """Parse an ISO datetime, returning None for empty or invalid values."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def effective_due_date(task: dict, now: datetime | None = None) -> datetime | None:
    """Return the task's effective due date after skip/snooze/season overrides."""
    del now
    override = task.get("next_due_override")
    if override:
        due = _parse(override)
        if due is None:
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

    snoozed = _parse(task.get("snoozed_until"))
    if snoozed is not None and snoozed > due:
        due = snoozed

    due = shift_into_season(due, task.get("active_months"))
    return due.replace(hour=0, minute=0, second=0, microsecond=0)


def day_delta(due: datetime, now: datetime) -> int:
    """Return whole calendar-day difference between due and now."""
    return (due.date() - now.date()).days


def snooze_active(task: dict, now: datetime) -> bool:
    """Return True while an explicit snooze (days or hours) is still running."""
    snoozed = _parse(task.get("snoozed_until"))
    return snoozed is not None and snoozed > now


def is_due(task: dict, now: datetime) -> bool:
    """Return True when the task should be shown as needing attention now."""
    due = effective_due_date(task, now)
    if due is None:
        return True
    if snooze_active(task, now):
        return False
    return day_delta(due, now) <= 0


def overdue_days(task: dict, now: datetime) -> int:
    """Return how many days the task is overdue (0 when not overdue)."""
    due = effective_due_date(task, now)
    if due is None:
        return 0
    return max(0, -day_delta(due, now))


def priority_of(task: dict) -> str:
    """Return a valid priority for a task."""
    value = task.get("priority") or DEFAULT_PRIORITY
    return value if value in PRIORITIES else DEFAULT_PRIORITY


def priority_score(task: dict, now: datetime) -> int:
    """
    Return the ordering score used to pick the next task.

    Base weight from priority (high 100, normal 50, low 0) plus 5 points per
    overdue day, capped at 10 days, so a long-neglected low-priority task
    eventually catches up with a freshly due normal one.
    """
    days = min(overdue_days(task, now), OVERDUE_POINTS_MAX_DAYS)
    return PRIORITY_WEIGHTS[priority_of(task)] + days * OVERDUE_POINTS_PER_DAY


def due_queue(tasks: list[dict], now: datetime) -> list[dict]:
    """Return due tasks ordered by score, then overdue days, then duration."""

    def sort_key(task: dict) -> tuple[int, int, int]:
        duration = task.get("duration_minutes")
        return (
            -priority_score(task, now),
            -overdue_days(task, now),
            int(duration) if duration else 10_000,
        )

    return sorted((t for t in tasks if is_due(t, now)), key=sort_key)


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
    if delta <= DUE_SOON_DAYS:
        return "due_soon"
    return "later"
