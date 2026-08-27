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
from .schedule import calculate_next_due, effective_due_date

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

STORAGE_KEY = f"{const.DOMAIN}.storage"
STORAGE_VERSION_MAJOR = 1
STORAGE_VERSION_MINOR = 2


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
        return cls(**clean)


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

        for key, value in updated.items():
            if key == "labels":
                continue
            normalized_value = value or None if key in {
                "tag_id",
                "description",
                "url",
                "source_entity_id",
                "source_state",
            } else value
            if hasattr(task, key):
                setattr(task, key, normalized_value)
                entity.task[key] = normalized_value

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
        task.last_performed = performed_date_str
        task.snoozed_until = None
        task.next_due_override = None
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

    def snooze_task(self, task_id: str, days: int) -> None:
        """Temporarily postpone a task without changing its completion history."""
        if days < 1:
            msg = "Snooze days must be greater than zero."
            raise RuntimeError(msg)
        entity, task = self._entity_and_task(task_id)
        snoozed = (dt_util.now() + timedelta(days=days)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
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
        task.next_due_override = calculate_next_due(
            due, task.interval_value, task.interval_type
        ).isoformat()
        task.snoozed_until = None
        entity.task.update(attr.asdict(task))
        self.hass.async_create_task(entity.async_update_ha_state(force_refresh=True))
        self.hass.bus.async_fire(
            const.EVENT_TASK_SKIPPED,
            {"task_id": task_id, "title": task.title},
        )
        self._save()

    def statistics(self) -> dict[str, int]:
        """Return lightweight aggregate statistics."""
        completed = sum(len(task.history) for task in self._tasks.values())
        skipped = sum(len(task.skipped) for task in self._tasks.values())
        snoozed = sum(bool(task.snoozed_until) for task in self._tasks.values())
        return {
            "tasks": len(self._tasks),
            "completed": completed,
            "skipped": skipped,
            "snoozed": snoozed,
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
