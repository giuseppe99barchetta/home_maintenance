"""Next-task sensor for Home Maintenance."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.util import dt as dt_util

from . import const
from .schedule import due_queue, overdue_days, priority_of, priority_score
from .streak import TRACKED_PRIORITY, compute_streak

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

SCAN_INTERVAL = timedelta(minutes=1)
QUEUE_ATTRIBUTE_LIMIT = 25


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,  # noqa: ARG001
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Home Maintenance sensor platform."""
    async_add_entities(
        [HomeMaintenanceNextTaskSensor(hass), HomeMaintenanceStreakSensor(hass)],
        update_before_add=True,
    )


def _hub_device_info() -> DeviceInfo:
    """Return the Home Maintenance hub device."""
    return DeviceInfo(
        identifiers={(const.DOMAIN, const.DEVICE_KEY)},
        name=const.NAME,
        model=const.NAME,
        sw_version=const.VERSION,
        manufacturer=const.MANUFACTURER,
    )


class HomeMaintenanceNextTaskSensor(SensorEntity):
    """The single most important due task, plus the ordered queue."""

    _attr_has_entity_name = True
    _attr_translation_key = "next_task"
    _attr_icon = "mdi:clipboard-text-clock"
    _attr_unique_id = f"{const.DOMAIN}_next_task"

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the sensor."""
        self.hass = hass
        # Stable, language-independent entity ID for automations and dashboards.
        self.entity_id = f"sensor.{const.DOMAIN}_next_task"
        self._attr_native_value = None
        self._attr_extra_state_attributes = {"queue": [], "due_count": 0}

    @property
    def device_info(self) -> DeviceInfo:
        """Attach the sensor to the Home Maintenance hub device."""
        return _hub_device_info()

    def _entity_id_for(self, registry: er.EntityRegistry, task_id: str) -> str | None:
        """Return the binary_sensor entity ID of a task."""
        return registry.async_get_entity_id(BINARY_SENSOR_DOMAIN, const.DOMAIN, task_id)

    async def async_update(self) -> None:
        """Recompute the queue from the task store."""
        data = self.hass.data.get(const.DOMAIN) or {}
        store = data.get("store")
        if store is None:
            return
        now = dt_util.now()
        registry = er.async_get(self.hass)
        queue: list[dict[str, Any]] = [
            {
                "entity_id": self._entity_id_for(registry, task["id"]),
                "task_id": task["id"],
                "title": task["title"],
                "priority": priority_of(task),
                "score": priority_score(task, now),
                "overdue_days": overdue_days(task, now),
                "duration_minutes": task.get("duration_minutes"),
            }
            for task in due_queue(store.get_all(), now)
        ]
        top = queue[0] if queue else None
        self._attr_native_value = top["title"] if top else None
        self._attr_extra_state_attributes = {
            **(top or {}),
            "due_count": len(queue),
            "queue": queue[:QUEUE_ATTRIBUTE_LIMIT],
        }


class HomeMaintenanceStreakSensor(SensorEntity):
    """Consecutive weeks in which no high-priority task was left overdue."""

    _attr_has_entity_name = True
    _attr_translation_key = "streak"
    _attr_icon = "mdi:fire"
    _attr_unique_id = f"{const.DOMAIN}_streak"
    _attr_native_unit_of_measurement = "w"

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self.entity_id = f"sensor.{const.DOMAIN}_streak"
        self._attr_native_value = 0
        self._attr_extra_state_attributes = {}

    @property
    def device_info(self) -> DeviceInfo:
        """Attach the sensor to the Home Maintenance hub device."""
        return _hub_device_info()

    async def async_update(self) -> None:
        """Recompute the streak from the stored history."""
        data = self.hass.data.get(const.DOMAIN) or {}
        store = data.get("store")
        if store is None:
            return
        streak = compute_streak(store.get_all(), dt_util.now())
        self._attr_native_value = streak.current
        self._attr_extra_state_attributes = {
            "best": streak.best,
            "current_week_ok": streak.current_week_ok,
            "weeks_tracked": streak.weeks_tracked,
            "tracked_tasks": streak.tracked_tasks,
            "tracked_priority": TRACKED_PRIORITY,
            "recent_weeks": list(streak.recent_weeks),
        }
