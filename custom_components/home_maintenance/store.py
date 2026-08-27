"""Store Home Maintenance configuration."""

import logging
from datetime import datetime

import attr
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry, storage
from homeassistant.util import dt as dt_util

from . import const
from .binary_sensor import HomeMaintenanceSensor

_LOGGER = logging.getLogger(__name__)

STORAGE_KEY = f"{const.DOMAIN}.storage"
STORAGE_VERSION_MAJOR = 1
STORAGE_VERSION_MINOR = 1


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
        """Load tasks from storage."""
        data = await self._store.async_load()
        if data is None:
            return

        self._tasks = {
            task_data["id"]: HomeMaintenanceTask(**task_data) for task_data in data
        }

    def get_all(self) -> list[dict]:
        """Return all tasks."""
        return [attr.asdict(task) for task in self._tasks.values()]

    def get(self, task_id: str) -> dict | None:
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

    def get_by_tag_uuid(self, tag_uuid: str) -> list[dict]:
        """Return tasks associated with a tag UUID."""
        tag_uuids = self._get_tag_uuids()
        return [
            attr.asdict(task)
            for task in self._tasks.values()
            if task.tag_id and tag_uuids.get(task.tag_id) == tag_uuid
        ]

    def get_by_tag_id(self, tag_id: str) -> list[dict]:
        """Return tasks associated with a tag entity ID."""
        return [
            attr.asdict(task) for task in self._tasks.values() if task.tag_id == tag_id
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

    def update_task(self, task_id: str, updated: dict) -> None:
        """Update an existing task and keep its Home Assistant entity in sync."""
        entity = self.hass.data[const.DOMAIN]["entities"].get(task_id)
        task = self._tasks.get(task_id)

        if entity is None or task is None:
            msg = "Task not found."
            raise RuntimeError(msg)

        for key, value in updated.items():
            if key == "labels":
                continue
            normalized_value = value or None if key == "tag_id" else value
            entity.task[key] = normalized_value
            if hasattr(task, key):
                setattr(task, key, normalized_value)

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

    def update_last_performed(
        self, task_id: str, performed_date: datetime | None = None
    ) -> None:
        """Update a task's last-performed date."""
        entity = self.hass.data[const.DOMAIN]["entities"].get(task_id)
        task = self._tasks.get(task_id)

        if entity is None or task is None:
            msg = "Task not found."
            raise RuntimeError(msg)

        if performed_date is None:
            performed_date = dt_util.now()
        performed_date_str = performed_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        ).isoformat()

        entity.task["last_performed"] = performed_date_str
        task.last_performed = performed_date_str
        self.hass.async_create_task(entity.async_update_ha_state(force_refresh=True))
        self._save()

    def _save(self) -> None:
        """Persist tasks without blocking the caller."""
        self.hass.async_create_task(
            self._store.async_save([attr.asdict(task) for task in self._tasks.values()])
        )
