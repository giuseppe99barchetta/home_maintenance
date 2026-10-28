"""Store Home Maintenance configuration."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

import attr
from homeassistant.helpers import entity_registry, storage
from homeassistant.util import dt as dt_util

from . import const
from .binary_sensor import HomeMaintenanceSensor
from .schedule import (
    DEFAULT_PRIORITY,
    DEFAULT_SCHEDULE_MODE,
    PRIORITIES,
    SCHEDULE_MODES,
    calculate_next_due,
    effective_due_date,
    next_fixed_occurrence,
    normalize_months,
)
from .streak import compute_streak

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

STORAGE_KEY = f"{const.DOMAIN}.storage"
STORAGE_VERSION_MAJOR = 1
STORAGE_VERSION_MINOR = 2

# Changing any of these starts a new fixed-rhythm series.
_ANCHOR_RESET_KEYS = {
    "schedule_mode",
    "interval_value",
    "interval_type",
    "last_performed",
    "next_due_override",
}


@attr.s(slots=True)
class HomeMaintenanceTask:
    """Represent a single home maintenance task."""

    id: str = attr.ib()
    title: str = attr.ib()
    interval_value: int = attr.ib()
    interval_type: str = attr.ib()
    last_performed: str = attr.ib()
    tag_id: str | None = attr.ib(default=None)
    icon: str | None = attr.ib(default=None)
    description: str | None = attr.ib(default=None)
    url: str | None = attr.ib(default=None)
    snoozed_until: str | None = attr.ib(default=None)
    next_due_override: str | None = attr.ib(default=None)
    history: list[str] = attr.ib(factory=list)
    skipped: list[str] = attr.ib(factory=list)
    notify_enabled: bool = attr.ib(default=False)
    notify_before_days: int = attr.ib(default=0)
    last_notified: str | None = attr.ib(default=None)
    source_entity_id: str | None = attr.ib(default=None)
    source_state: str | None = attr.ib(default=None)
    priority: str = attr.ib(default=DEFAULT_PRIORITY)
    duration_minutes: int | None = attr.ib(default=None)
    schedule_mode: str = attr.ib(default=DEFAULT_SCHEDULE_MODE)
    active_months: list[int] = attr.ib(factory=list)
    schedule_anchor: str | None = attr.ib(default=None)
    checklist: list[str] = attr.ib(factory=list)
    checklist_done: list[int] = attr.ib(factory=list)
    checklist_autocomplete: bool = attr.ib(default=True)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> HomeMaintenanceTask:
        """Create a task from old or current storage data."""
        known = {field.name for field in attr.fields(cls)}
        clean = {key: val for key, val in value.items() if key in known}
        clean.setdefault("tag_id", None)
        clean.setdefault("icon", "mdi:calendar-check")
        clean.setdefault("description", None)
        clean.setdefault("url", None)
        clean.setdefault("snoozed_until", None)
        clean.setdefault("next_due_override", None)
        clean.setdefault("history", [])
        clean.setdefault("skipped", [])
        clean.setdefault("notify_enabled", False)
        clean.setdefault("notify_before_days", 0)
        clean.setdefault("last_notified", None)
        clean.setdefault("source_entity_id", None)
        clean.setdefault("source_state", None)
        clean["priority"] = (
            clean.get("priority")
            if clean.get("priority") in PRIORITIES
            else DEFAULT_PRIORITY
        )
        clean["schedule_mode"] = (
            clean.get("schedule_mode")
            if clean.get("schedule_mode") in SCHEDULE_MODES
            else DEFAULT_SCHEDULE_MODE
        )
        clean["duration_minutes"] = _clean_duration(clean.get("duration_minutes"))
        clean["active_months"] = normalize_months(clean.get("active_months"))
        clean["checklist"] = normalize_checklist(clean.get("checklist"))
        clean["checklist_done"] = normalize_done(
            clean.get("checklist_done"), len(clean["checklist"])
        )
        clean["checklist_autocomplete"] = bool(
            clean.get("checklist_autocomplete", True)
        )
        return cls(**clean)


MAX_CHECKLIST_STEPS = 30
MAX_STEP_LENGTH = 120


def normalize_checklist(value: Any) -> list[str]:
    """Return trimmed, non-empty step titles (a string is split by lines)."""
    if isinstance(value, str):
        value = value.splitlines()
    if not isinstance(value, (list, tuple)):
        return []
    steps = [
        str(step).strip()[:MAX_STEP_LENGTH]
        for step in value
        if isinstance(step, (str, int, float))
    ]
    return [step for step in steps if step][:MAX_CHECKLIST_STEPS]


def normalize_done(value: Any, total: int) -> list[int]:
    """Return sorted, unique, in-range step indices."""
    if not isinstance(value, (list, tuple)):
        return []
    done = set()
    for index in value:
        try:
            number = int(index)
        except (TypeError, ValueError):
            continue
        if 0 <= number < total:
            done.add(number)
    return sorted(done)


def _clean_duration(value: Any) -> int | None:
    """Return a positive duration in minutes, or None."""
    try:
        minutes = int(value)
    except (TypeError, ValueError):
        return None
    return minutes if minutes > 0 else None


_EMPTY_TO_NONE = {"tag_id", "description", "url", "source_entity_id", "source_state"}


_ALLOWED_VALUES = {"priority": PRIORITIES, "schedule_mode": SCHEDULE_MODES}
_NORMALIZERS = {
    "active_months": normalize_months,
    "duration_minutes": _clean_duration,
    "checklist": normalize_checklist,
    "checklist_autocomplete": bool,
}


def _normalize_update(
    task: HomeMaintenanceTask, key: str, value: Any, updated: dict[str, Any]
) -> tuple[bool, Any]:
    """Return (accepted, value) for one field of a task update."""
    if key in _ALLOWED_VALUES:
        return value in _ALLOWED_VALUES[key], value
    if key in _EMPTY_TO_NONE:
        value = value or None
    elif key in _NORMALIZERS:
        value = _NORMALIZERS[key](value)
    elif key == "checklist_done":
        total = len(normalize_checklist(updated.get("checklist", task.checklist)))
        value = normalize_done(value, total)
    return True, value


class TaskStore:
    """Hold and persist Home Maintenance task data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the storage."""
        self.hass = hass
        self._store = storage.Store(
            hass,
            STORAGE_VERSION_MAJOR,
            STORAGE_KEY,
            minor_version=STORAGE_VERSION_MINOR,
        )
        self._tasks: dict[str, HomeMaintenanceTask] = {}

    async def async_load(self) -> None:
        """Load tasks from storage and transparently migrate older records."""
        data = await self._store.async_load()
        if data is None:
            return
        self._tasks = {
            task_data["id"]: HomeMaintenanceTask.from_dict(task_data)
            for task_data in data
            if isinstance(task_data, dict) and task_data.get("id")
        }

    def get_all(self) -> list[dict[str, Any]]:
        """Return all tasks."""
        return [attr.asdict(task) for task in self._tasks.values()]

    def get(self, task_id: str) -> dict[str, Any] | None:
        """Return a single task if it exists."""
        task = self._tasks.get(task_id)
        return attr.asdict(task) if task is not None else None

    def _get_tag_uuids(self) -> dict[str, str]:
        """Return a mapping of task tag entity IDs to tag UUIDs."""
        registry = entity_registry.async_get(self.hass)
        tag_ids = [task.tag_id for task in self._tasks.values() if task.tag_id]
        tag_uuids: dict[str, str] = {}
        for tag_id in tag_ids:
            if tag_id in tag_uuids:
                continue
            entry = registry.async_get(tag_id)
            if entry:
                tag_uuids[tag_id] = entry.unique_id
        return tag_uuids

    def get_by_tag_uuid(self, tag_uuid: str) -> list[dict[str, Any]]:
        """Return tasks associated with a tag UUID."""
        tag_uuids = self._get_tag_uuids()
        return [
            attr.asdict(task)
            for task in self._tasks.values()
            if task.tag_id and tag_uuids.get(task.tag_id) == tag_uuid
        ]

    def get_by_tag_id(self, tag_id: str) -> list[dict[str, Any]]:
        """Return tasks associated with a tag entity ID."""
        return [
            attr.asdict(task) for task in self._tasks.values() if task.tag_id == tag_id
        ]

    def get_by_source_entity(self, entity_id: str) -> list[dict[str, Any]]:
        """Return tasks that can be completed by a source entity."""
        return [
            attr.asdict(task)
            for task in self._tasks.values()
            if task.source_entity_id == entity_id and task.source_state
        ]

    def add(self, task: HomeMaintenanceTask, labels: list[str] | None = None) -> str:
        """Add a new task and its entity."""
        add_entities = self.hass.data[const.DOMAIN].get("add_entities")
        if not add_entities:
            msg = "add_entities not registered yet."
            raise RuntimeError(msg)
        device_id = self.hass.data[const.DOMAIN].get("device_id")
        if not device_id:
            msg = "Device ID not available."
            raise RuntimeError(msg)
        if task.id in self._tasks:
            msg = f"Task {task.id} already exists."
            raise RuntimeError(msg)

        entity = HomeMaintenanceSensor(
            self.hass, attr.asdict(task), device_id, labels=labels
        )
        add_entities([entity])
        self._tasks[task.id] = task
        self.hass.data[const.DOMAIN]["entities"][task.id] = entity
        self._save()
        return entity.unique_id

    def delete(self, task_id: str) -> None:
        """Remove a task, its entity-registry entry and in-memory entity reference."""
        if task_id not in self._tasks:
            msg = f"No task found with ID {task_id}."
            raise RuntimeError(msg)

        registry = entity_registry.async_get(self.hass)
        entity_entry = next(
            (
                entry
                for entry in registry.entities.values()
                if entry.unique_id == task_id and entry.platform == const.DOMAIN
            ),
            None,
        )
        if entity_entry is not None:
            registry.async_remove(entity_entry.entity_id)

        self._tasks.pop(task_id, None)
        self.hass.data[const.DOMAIN]["entities"].pop(task_id, None)
        self._save()

    def update_task(self, task_id: str, updated: dict[str, Any]) -> None:
        """Update an existing task and keep its Home Assistant entity in sync."""
        entity = self.hass.data[const.DOMAIN]["entities"].get(task_id)
        task = self._tasks.get(task_id)
        if entity is None or task is None:
            msg = "Task not found."
            raise RuntimeError(msg)

        rhythm_before = {key: getattr(task, key) for key in _ANCHOR_RESET_KEYS}
        for key, value in updated.items():
            if key == "labels" or not hasattr(task, key):
                continue
            accepted, normalized_value = _normalize_update(task, key, value, updated)
            if not accepted:
                continue
            if key == "checklist" and normalized_value != task.checklist:
                # Different steps: progress of the old list is meaningless.
                task.checklist_done = []
                entity.task["checklist_done"] = []
            setattr(task, key, normalized_value)
            entity.task[key] = normalized_value

        rhythm_after = {key: getattr(task, key) for key in _ANCHOR_RESET_KEYS}
        if rhythm_after != rhythm_before and "schedule_anchor" not in updated:
            task.schedule_anchor = None
            entity.task["schedule_anchor"] = None

        if "title" in updated:
            entity._attr_name = str(updated["title"])  # noqa: SLF001

        if "labels" in updated:
            registry = entity_registry.async_get(self.hass)
            if registry.async_get(entity.entity_id):
                registry.async_update_entity(
                    entity.entity_id,
                    labels=set(updated["labels"]),
                )

        self.hass.async_create_task(entity.async_update_ha_state(force_refresh=True))
        self._save()

    def complete_task(
        self,
        task_id: str,
        performed_date: datetime | None = None,
        *,
        source: str = "manual",
    ) -> None:
        """Complete a task and append an immutable completion-history entry."""
        entity, task = self._entity_and_task(task_id)
        performed_date = performed_date or dt_util.now()
        performed_date_str = performed_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        ).isoformat()
        next_override = None
        if task.schedule_mode == "fixed":
            next_override = self._next_fixed_due(task, performed_date)
        task.last_performed = performed_date_str
        task.snoozed_until = None
        task.next_due_override = next_override
        task.checklist_done = []
        task.history.append(performed_date_str)
        entity.task.update(attr.asdict(task))
        self.hass.async_create_task(entity.async_update_ha_state(force_refresh=True))
        self.hass.bus.async_fire(
            const.EVENT_TASK_COMPLETED,
            {"task_id": task_id, "title": task.title, "source": source},
        )
        self._save()

    def update_last_performed(
        self, task_id: str, performed_date: datetime | None = None
    ) -> None:
        """Backward-compatible alias for completing a task."""
        self.complete_task(task_id, performed_date)

    def snooze_task(self, task_id: str, days: int = 0, hours: int = 0) -> None:
        """
        Temporarily postpone a task without changing its completion history.

        Day snoozes end at local midnight of the target day; hour snoozes keep
        the exact time so a task can come back later the same day.
        """
        if days < 0 or hours < 0 or days + hours < 1:
            msg = "Snooze must be at least one day or one hour."
            raise RuntimeError(msg)
        entity, task = self._entity_and_task(task_id)
        snoozed = dt_util.now() + timedelta(days=days, hours=hours)
        if not hours:
            snoozed = snoozed.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            snoozed = snoozed.replace(second=0, microsecond=0)
        task.snoozed_until = snoozed.isoformat()
        entity.task["snoozed_until"] = task.snoozed_until
        self.hass.async_create_task(entity.async_update_ha_state(force_refresh=True))
        self._save()

    def skip_task(self, task_id: str) -> None:
        """Skip only the current occurrence without pretending it was completed."""
        entity, task = self._entity_and_task(task_id)
        task_dict = attr.asdict(task)
        due = effective_due_date(task_dict, dt_util.now())
        if due is None:
            msg = "Could not calculate the current due date."
            raise RuntimeError(msg)
        task.skipped.append(due.isoformat())
        if task.schedule_mode == "fixed":
            task.next_due_override = self._next_fixed_due(task, due)
        else:
            task.next_due_override = calculate_next_due(
                due, task.interval_value, task.interval_type
            ).isoformat()
        task.snoozed_until = None
        task.checklist_done = []
        entity.task.update(attr.asdict(task))
        self.hass.async_create_task(entity.async_update_ha_state(force_refresh=True))
        self.hass.bus.async_fire(
            const.EVENT_TASK_SKIPPED,
            {"task_id": task_id, "title": task.title},
        )
        self._save()

    def check_step(
        self,
        task_id: str,
        step: int | str,
        checked: bool | None = None,
    ) -> bool:
        """
        Tick or untick one checklist step of the current occurrence.

        ``step`` is a 0-based index or a step title (case-insensitive);
        ``checked=None`` toggles. Returns True when ticking the last open step
        completed the whole task (only with ``checklist_autocomplete``).
        """
        entity, task = self._entity_and_task(task_id)
        if not task.checklist:
            msg = "This task has no checklist."
            raise RuntimeError(msg)
        index = self._step_index(task, step)
        done = set(task.checklist_done)
        should_check = index not in done if checked is None else checked
        if should_check:
            done.add(index)
        else:
            done.discard(index)
        task.checklist_done = sorted(done)
        self.hass.bus.async_fire(
            const.EVENT_STEP_CHECKED,
            {
                "task_id": task_id,
                "title": task.title,
                "step": task.checklist[index],
                "index": index,
                "checked": should_check,
                "done": len(task.checklist_done),
                "total": len(task.checklist),
            },
        )
        if (
            should_check
            and task.checklist_autocomplete
            and len(task.checklist_done) == len(task.checklist)
        ):
            self.complete_task(task_id, source="checklist")
            return True
        entity.task["checklist_done"] = list(task.checklist_done)
        self.hass.async_create_task(entity.async_update_ha_state(force_refresh=True))
        self._save()
        return False

    @staticmethod
    def _step_index(task: HomeMaintenanceTask, step: int | str) -> int:
        """Resolve a step index or title to a valid 0-based index."""
        if isinstance(step, int) and not isinstance(step, bool):
            if 0 <= step < len(task.checklist):
                return step
        elif isinstance(step, str):
            wanted = step.strip().casefold()
            for index, title in enumerate(task.checklist):
                if title.casefold() == wanted:
                    return index
        msg = f"Checklist step not found: {step}"
        raise RuntimeError(msg)

    def statistics(self) -> dict[str, Any]:
        """Return lightweight aggregate statistics."""
        completed = sum(len(task.history) for task in self._tasks.values())
        skipped = sum(len(task.skipped) for task in self._tasks.values())
        snoozed = sum(bool(task.snoozed_until) for task in self._tasks.values())
        return {
            "tasks": len(self._tasks),
            "completed": completed,
            "skipped": skipped,
            "snoozed": snoozed,
            "streak": compute_streak(self.get_all(), dt_util.now()).as_dict(),
        }

    def export_data(self) -> list[dict[str, Any]]:
        """Return portable task data."""
        return self.get_all()

    def import_data(self, tasks: list[dict[str, Any]]) -> int:
        """Import task data, updating existing tasks and creating new entities."""
        imported = 0
        for raw in tasks:
            task = HomeMaintenanceTask.from_dict(raw)
            if task.id in self._tasks:
                self.update_task(task.id, attr.asdict(task))
            else:
                self.add(task)
            imported += 1
        return imported

    def _next_fixed_due(
        self, task: HomeMaintenanceTask, completed: datetime
    ) -> str | None:
        """
        Return the next fixed-rhythm due date and remember the series anchor.

        The anchor is the first due date seen in fixed mode and is kept
        unclamped, so later occurrences are always anchor + k * interval.
        """
        current_due = effective_due_date(
            {**attr.asdict(task), "snoozed_until": None}, completed
        )
        if current_due is None:
            return None
        anchor = None
        if task.schedule_anchor:
            try:
                anchor = datetime.fromisoformat(task.schedule_anchor)
            except ValueError:
                anchor = None
        if anchor is None:
            anchor = current_due
            task.schedule_anchor = anchor.isoformat()
        return next_fixed_occurrence(
            anchor,
            completed,
            task.interval_value,
            task.interval_type,
            current_due=current_due,
        ).isoformat()

    def _entity_and_task(
        self, task_id: str
    ) -> tuple[HomeMaintenanceSensor, HomeMaintenanceTask]:
        """Return a loaded entity and task or raise a useful error."""
        entity = self.hass.data[const.DOMAIN]["entities"].get(task_id)
        task = self._tasks.get(task_id)
        if entity is None or task is None:
            msg = "Task not found."
            raise RuntimeError(msg)
        return entity, task

    def _save(self) -> None:
        """Persist tasks without blocking the caller."""
        self.hass.async_create_task(
            self._store.async_save([attr.asdict(task) for task in self._tasks.values()])
        )
