"""
Weekly completion streaks for Home Maintenance.

A week (Monday to Sunday) is *kept* when, at the end of that week, no tracked
task was left overdue: every occurrence due in that week (or earlier) had been
completed or skipped by Sunday. Weeks without anything due are kept as well.

Everything is derived from the stored completion history, the skipped
occurrences and the current due date, so the result is the same after a
restart or an import. Snoozes are not part of the history, so a past snooze is
seen as the task being late.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from itertools import pairwise
from typing import TYPE_CHECKING

from .schedule import calculate_next_due, effective_due_date, priority_of

if TYPE_CHECKING:
    from collections.abc import Iterable

MAX_WEEKS = 520
TRACKED_PRIORITY = "high"
RECENT_WEEKS = 8


@dataclass(frozen=True)
class Occurrence:
    """One due occurrence of a task and the day it was dealt with."""

    due: date
    done: date | None


@dataclass(frozen=True)
class Streak:
    """Weekly streak summary."""

    current: int
    best: int
    current_week_ok: bool
    weeks_tracked: int
    tracked_tasks: int
    recent_weeks: tuple[bool, ...] = ()

    def as_dict(self) -> dict[str, int | bool | list[bool]]:
        """Return a JSON-friendly representation."""
        return {
            "current": self.current,
            "best": self.best,
            "current_week_ok": self.current_week_ok,
            "weeks_tracked": self.weeks_tracked,
            "tracked_tasks": self.tracked_tasks,
            "recent_weeks": list(self.recent_weeks),
        }


def week_start(day: date) -> date:
    """Return the Monday of the week containing ``day``."""
    return day - timedelta(days=day.weekday())


def _dates(values: Iterable[str] | None) -> list[date]:
    out = []
    for value in values or []:
        try:
            out.append(datetime.fromisoformat(value).date())
        except (TypeError, ValueError):
            continue
    return sorted(out)


def _next(day: date, value: int, kind: str) -> date:
    return calculate_next_due(
        datetime.combine(day, datetime.min.time()), value, kind
    ).date()


def task_occurrences(task: dict, now: datetime) -> list[Occurrence]:
    """Rebuild the due occurrences of a task from its history."""
    history = _dates(task.get("history"))
    occurrences: list[Occurrence] = []
    try:
        value = int(task["interval_value"])
        kind = str(task["interval_type"])
    except (KeyError, TypeError, ValueError):
        return occurrences

    skipped = set(_dates(task.get("skipped")))
    for previous, current in pairwise(history):
        due = _next(previous, value, kind)
        # A skipped occurrence is dealt with on its own due day; the next
        # completion then answers the following occurrence.
        while due in skipped and due < current:
            occurrences.append(Occurrence(due=due, done=due))
            skipped.discard(due)
            due = _next(due, value, kind)
        occurrences.append(Occurrence(due=due, done=current))

    occurrences.extend(Occurrence(due=d, done=d) for d in sorted(skipped))

    pending = effective_due_date(task, now)
    if pending is not None and (not history or pending.date() > history[-1]):
        occurrences.append(Occurrence(due=pending.date(), done=None))
    return occurrences


def _outstanding_at(occurrences: list[Occurrence], day: date) -> bool:
    """Return True when something due on or before ``day`` was still open."""
    return any(
        occ.due <= day and (occ.done is None or occ.done > day) for occ in occurrences
    )


def compute_streak(
    tasks: list[dict], now: datetime, priority: str = TRACKED_PRIORITY
) -> Streak:
    """Return current and best weekly streaks for tasks of ``priority``."""
    tracked = [task for task in tasks if priority_of(task) == priority]
    occurrences: list[Occurrence] = []
    first_days: list[date] = []
    for task in tracked:
        occurrences.extend(task_occurrences(task, now))
        history = _dates(task.get("history"))
        if history:
            first_days.append(history[0])

    today = now.date()
    this_week = week_start(today)
    current_week_ok = not _outstanding_at(occurrences, today)
    if not first_days:
        return Streak(0, 0, current_week_ok, 0, len(tracked))

    start = max(week_start(min(first_days)), this_week - timedelta(weeks=MAX_WEEKS))
    kept: list[bool] = []
    week = start
    while week < this_week:
        kept.append(not _outstanding_at(occurrences, week + timedelta(days=6)))
        week += timedelta(weeks=1)

    current = 0
    for ok in reversed(kept):
        if not ok:
            break
        current += 1

    best = run = 0
    for ok in kept:
        run = run + 1 if ok else 0
        best = max(best, run)

    return Streak(
        current,
        best,
        current_week_ok,
        len(kept),
        len(tracked),
        tuple(kept[-RECENT_WEEKS:]),
    )
