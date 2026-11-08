"""
Points, challenges and weekly/monthly recaps for Home Maintenance.

Every completion earns points for whoever marked it (a Home Assistant person,
a Home Assistant user or a free name such as a Telegram account): 1, 2 or 3
points for a low, normal or high priority task, plus one bonus point when it
was done on or before its due day. Like the streak, everything is derived
from the stored history, so it survives restarts and imports.
"""

from __future__ import annotations

from calendar import monthrange
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Any

from .schedule import priority_of
from .streak import _dates, task_occurrences, week_start

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

POINTS = {"low": 1, "normal": 2, "high": 3}
ON_TIME_BONUS = 1
PERIODS = ("week", "month")

# Challenge -> standings field that decides it.
CHALLENGES = {"champion": "points", "punctual": "on_time", "firefighter": "high"}


def period_range(
    period: str, day: date, *, previous: bool = False
) -> tuple[date, date]:
    """Return the first and last day of the week or month containing ``day``."""
    if period == "week":
        start = week_start(day)
        if previous:
            start -= timedelta(weeks=1)
        return start, start + timedelta(days=6)
    start = day.replace(day=1)
    if previous:
        start = (start - timedelta(days=1)).replace(day=1)
    return start, start.replace(day=monthrange(start.year, start.month)[1])


def _completions(task: dict, now: datetime) -> list[tuple[date, str | None, bool]]:
    """Return (day, by, on_time) for every completion of a task."""
    due_by_done: dict[date, date] = {}
    for occ in task_occurrences(task, now):
        if occ.done is not None:
            due_by_done[occ.done] = max(occ.due, due_by_done.get(occ.done, occ.due))
    by = list(task.get("history_by") or [])
    out = []
    for index, value in enumerate(task.get("history") or []):
        days = _dates([value])
        if not days:
            continue
        due = due_by_done.get(days[0])
        # The first completion has no previous due date: count it as on time.
        who = by[index] if index < len(by) else None
        out.append((days[0], who, due is None or days[0] <= due))
    return out


def standings(tasks: list[dict], now: datetime, start: date, end: date) -> list[dict]:
    """Return per-person totals for completions between ``start`` and ``end``."""
    totals: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"points": 0, "completions": 0, "on_time": 0, "high": 0}
    )
    for task in tasks:
        priority = priority_of(task)
        for day, by, on_time in _completions(task, now):
            if not by or not start <= day <= end:
                continue
            # "a,b" = done together: everyone gets the full points.
            for who in by.split(","):
                row = totals[who]
                row["completions"] += 1
                row["points"] += POINTS[priority] + (ON_TIME_BONUS if on_time else 0)
                row["on_time"] += on_time
                row["high"] += priority == "high"
    rows = [{"who": who, **row} for who, row in totals.items()]
    return sorted(rows, key=lambda r: (-r["points"], -r["completions"], r["who"]))


def winners(rows: list[dict]) -> dict[str, list[str]]:
    """Return who won each challenge; ties share it, nobody wins with zero."""
    out = {}
    for challenge, field in CHALLENGES.items():
        best = max((row[field] for row in rows), default=0)
        out[challenge] = [row["who"] for row in rows if best and row[field] == best]
    return out


def display_name(hass: HomeAssistant, who: str) -> str:
    """Return the friendly name of a person entity, or the stored name."""
    state = hass.states.get(who) if who.startswith("person.") else None
    return state.name if state else who


async def async_resolve_by(
    hass: HomeAssistant, user: str | None = None, user_id: str | None = None
) -> str | None:
    """
    Return who completed a task.

    ``user`` is an explicit name or person entity (e.g. from a Telegram
    automation) and matches a person by name, so the same person on Home
    Assistant and Telegram counts once. ``user_id`` is the Home Assistant user
    from the call context.
    """
    people = hass.states.async_all("person")
    if user := (user or "").strip():

        def match(name: str) -> str:
            wanted = name.casefold()
            for state in people:
                if wanted in (state.entity_id, state.name.casefold()):
                    return state.entity_id
            return name

        # Comma-separated names mean "done together".
        names = [match(name.strip()) for name in user.split(",") if name.strip()]
        return ",".join(dict.fromkeys(names)) or None
    if not user_id:
        return None
    for state in people:
        if state.attributes.get("user_id") == user_id:
            return state.entity_id
    ha_user = await hass.auth.async_get_user(user_id)
    if ha_user is None or ha_user.system_generated:
        return None
    return ha_user.name


_TEXT = {
    "en": {
        "week": "Weekly recap",
        "month": "Monthly recap",
        "empty": "Nobody completed a task in this period.",
        "row": "{pos}. {name}: {points} pts ({completions} done, {on_time} on time)",
        "champion": "🏆 Champion",
        "punctual": "⏱️ Always on time",
        "firefighter": "🔥 High-priority hero",
    },
    "it": {
        "week": "Recap settimanale",
        "month": "Recap mensile",
        "empty": "Nessuno ha completato attività in questo periodo.",
        "row": "{pos}. {name}: {points} punti "
        "({completions} fatte, {on_time} puntuali)",
        "champion": "🏆 Campione",
        "punctual": "⏱️ Sempre puntuale",
        "firefighter": "🔥 Eroe dell'alta priorità",
    },
}


def recap_message(recap: dict, language: str) -> str:
    """Return a plain-text recap, ready for a notification or Telegram."""
    text = _TEXT["it" if language.startswith("it") else "en"]
    lines = [f"{text[recap['period']]} {recap['start']} → {recap['end']}"]
    if not recap["standings"]:
        return "\n".join([*lines, text["empty"]])
    lines += [
        text["row"].format(pos=pos, **row)
        for pos, row in enumerate(recap["standings"], start=1)
    ]
    lines += [
        f"{text[challenge]}: {', '.join(names)}"
        for challenge, names in recap["winners"].items()
        if names
    ]
    return "\n".join(lines)
