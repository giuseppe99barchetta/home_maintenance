"""Support for Home Maintenance binary sensors."""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from . import const
from .schedule import day_delta, effective_due_date

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,  # noqa: ARG001
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Home Maintenance binary sensor platform."""
    hass.data.setdefault(const.DOMAIN, {})
    hass.data[const.DOMAIN]["add_entities"] = async_add_entities

    device_id = hass.data[const.DOMAIN].get("device_id")
    store = hass.data[const.DOMAIN].get("store")
    entities = []
    for task in store.get_all():
        entity = HomeMaintenanceSensor(hass, task, device_id)
        entities.append(entity)
        hass.data[const.DOMAIN]["entities"][task["id"]] = entity
    async_add_entities(entities)


class HomeMaintenanceSensor(BinarySensorEntity):
    """Representation of a Home Maintenance binary sensor."""

    def __init__(
        self,
        hass: HomeAssistant,
        task: dict,
        device_id: str,
        labels: list[str] | None = None,
    ) -> None:
        """Initialize the Home Maintenance sensor."""
        self.hass = hass
        self.task = task
        self._attr_name = task["title"]
        self._attr_unique_id = task["id"]
        self._device_id = device_id
        self._labels = labels or []
        self._update_state()

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device information for this sensor."""
        return DeviceInfo(
            identifiers={(const.DOMAIN, const.DEVICE_KEY)},
            name=const.NAME,
            model=const.NAME,
            sw_version=const.VERSION,
            manufacturer=const.MANUFACTURER,
        )

    @property
    def icon(self) -> str | None:
        """Return the icon for the task."""
        return self.task.get("icon") or "mdi:calendar-check"

    def _update_state(self) -> None:
        """Refresh due state and rich task attributes."""
        now = dt_util.now()
        due = effective_due_date(self.task, now)
        delta = day_delta(due, now) if due else None
        self._attr_is_on = due is None or delta <= 0

        attrs = {
            "last_performed": self.task.get("last_performed"),
            "interval_value": self.task.get("interval_value"),
            "interval_type": self.task.get("interval_type"),
            "next_due": due.isoformat() if due else "unknown",
            "days_remaining": delta if delta is not None else None,
            "overdue_days": abs(delta) if delta is not None and delta < 0 else 0,
            "snoozed_until": self.task.get("snoozed_until"),
            "history_count": len(self.task.get("history", [])),
            "skipped_count": len(self.task.get("skipped", [])),
            "notify_enabled": self.task.get("notify_enabled", False),
            "notify_before_days": self.task.get("notify_before_days", 0),
            "description": self.task.get("description"),
            "url": self.task.get("url"),
            "source_entity_id": self.task.get("source_entity_id"),
            "source_state": self.task.get("source_state"),
        }
        if self.task.get("tag_id"):
            attrs["tag_id"] = self.task["tag_id"]
        self._attr_extra_state_attributes = attrs

    async def async_update(self) -> None:
        """Get the latest state of the sensor."""
        self._update_state()

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to Home Assistant."""
        if self._labels:
            registry = er.async_get(self.hass)
            if registry.async_get(self.entity_id):
                registry.async_update_entity(self.entity_id, labels=set(self._labels))
