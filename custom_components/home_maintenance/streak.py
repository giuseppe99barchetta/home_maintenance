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

from .schedule import (
    calculate_next_due,
    effective_due_date,
    next_fixed_occurrence,
    normalize_months,
    priority_of,
)

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


def _dt(day: date) -> datetime:
    return datetime.combine(day, datetime.min.time())


def _next(day: date, value: int, kind: str) -> date:
    return calculate_next_due(_dt(day), value, kind).date()


@dataclass(frozen=True)
class _Rules:
    """The scheduling rules TaskStore applies to a task."""

    value: int
    kind: str
    months: tuple[int, ...]
    anchor: date | None

    @classmethod
    def of(cls, task: dict) -> _Rules:
        anchor = None
        if task.get("schedule_mode") == "fixed":
            anchors = _dates([task.get("schedule_anchor")])
            anchor = anchors[0] if anchors else None
        return cls(
            int(task["interval_value"]),
            str(task["interval_type"]),
            tuple(normalize_months(task.get("active_months"))),
            anchor,
        )

    def next_due(self, completed: date, answered_due: date | None) -> date:
        """Due date of the occurrence that follows a completion."""
        plain = _next(completed, self.value, self.kind)
        if self.anchor is not None and plain > self.anchor:
            current = _dt(answered_due) if answered_due else None
            plain = next_fixed_occurrence(
                _dt(self.anchor),
                _dt(completed),
                self.value,
                self.kind,
                current_due=current,
            ).date()
        return self.into_season(plain)

    def active(self, day: date) -> bool:
        return not self.months or day.month in self.months

    def into_season(self, day: date) -> date:
        """First day of the next active month when ``day`` is off season."""
        if self.active(day):
            return day
        month = day.replace(day=1)
        for _ in range(12):
            month = (month + timedelta(days=32)).replace(day=1)
            if self.active(month):
                return month
        return day

    def season_end(self, day: date) -> date | None:
        """First day of the first inactive month after ``day``."""
        if not self.months:
            return None
        month = day.replace(day=1)
        for _ in range(12):
            month = (month + timedelta(days=32)).replace(day=1)
            if not self.active(month):
                return month
        return None

    def split(self, due: date, done: date | None, today: date) -> list[Occurrence]:
        """
        Split an occurrence at season ends, like effective_due_date does.

        A task still open when its season ends stops being overdue and waits
        for the first day of the next active month.
        """
        out: list[Occurrence] = []
        for _ in range(24):
            end = self.season_end(due)
            if end is None or (done is not None and done < end) or end > today:
                out.append(Occurrence(due=due, done=done))
                return out
            out.append(Occurrence(due=due, done=end))
            due = self.into_season(end)
        out.append(Occurrence(due=due, done=done))
        return out


def task_occurrences(task: dict, now: datetime) -> list[Occurrence]:
    """Rebuild the due occurrences of a task from its history and rules."""
    history = _dates(task.get("history"))
    occurrences: list[Occurrence] = []
    try:
        rules = _Rules.of(task)
    except (KeyError, TypeError, ValueError):
        return occurrences
    today = now.date()

    skipped = set(_dates(task.get("skipped")))
    answered: date | None = None
    for previous, current in pairwise(history):
        due = rules.next_due(previous, answered)
        # A skipped occurrence is dealt with on its own due day; the next
        # completion then answers the following occurrence.
        while due in skipped and due < current:
            occurrences.append(Occurrence(due=due, done=due))
            skipped.discard(due)
            due = rules.next_due(due, due)
        occurrences.extend(rules.split(due, current, today))
        answered = due

    occurrences.extend(Occurrence(due=d, done=d) for d in sorted(skipped))

    # Without ``now`` this is the scheduled date before any off-season
    # deferral; split() applies the deferral week by week instead.
    pending = effective_due_date(task)
    if pending is not None and (not history or pending.date() > history[-1]):
        occurrences.extend(rules.split(pending.date(), None, today))
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
