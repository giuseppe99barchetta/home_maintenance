"""Support for Home Maintenance."""

import logging
import uuid
from datetime import datetime
from typing import cast

from homeassistant.components import persistent_notification
from homeassistant.components.binary_sensor import DOMAIN as PLATFORM
from homeassistant.components.tag.const import EVENT_TAG_SCANNED
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.core import Event, HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_registry import RegistryEntry  # noqa: TC002
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import dt as dt_util

from . import const
from .panel import async_register_panel, async_unregister_panel
from .schedule import day_delta, effective_due_date
from .store import HomeMaintenanceTask, TaskStore
from .websocket import async_register_websockets

_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = const.CONFIG_SCHEMA


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:  # noqa: ARG001
    """Set up integration-wide services and WebSocket commands once."""
    await async_register_websockets(hass)
    register_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Home Maintenance config entry."""

    @callback
    def handle_tag_scanned_event(event: Event) -> None:
        """Complete tasks associated with a scanned NFC tag."""
        tag_id = event.data.get("tag_id")
        store = _store(hass)
        if store is None or not tag_id:
            return
        for task in store.get_by_tag_uuid(tag_id):
            store.complete_task(task["id"], source="nfc")

    @callback
    def handle_state_changed(event: Event) -> None:
        """Complete tasks when their configured source reaches its target state."""
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")
        store = _store(hass)
        if store is None or not entity_id or new_state is None:
            return
        for task in store.get_by_source_entity(entity_id):
            if new_state.state == task.get("source_state"):
                store.complete_task(task["id"], source="entity")

    @callback
    def check_notifications(_now: datetime | None = None) -> None:
        """Notify once per day for tasks inside their notification window."""
        store = _store(hass)
        if store is None:
            return
        now = dt_util.now()
        today = now.date().isoformat()
        for task in store.get_all():
            if not task.get("notify_enabled") or task.get("last_notified") == today:
                continue
            due = effective_due_date(task, now)
            if due is None:
                continue
            delta = day_delta(due, now)
            before = int(task.get("notify_before_days", 0))
            if delta > before:
                continue
            if delta < 0:
                timing = f"overdue by {abs(delta)} day(s)"
            elif delta == 0:
                timing = "due today"
            else:
                timing = f"due in {delta} day(s)"
            persistent_notification.async_create(
                hass,
                f"{task['title']} is {timing}.",
                title="Home Maintenance",
                notification_id=f"home_maintenance_{task['id']}",
            )
            store.update_task(task["id"], {"last_notified": today})
            hass.bus.async_fire(
                const.EVENT_TASK_DUE,
                {"task_id": task["id"], "title": task["title"], "days": delta},
            )

    task_store = TaskStore(hass)
    await task_store.async_load()

    device_registry = dr.async_get(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(const.DOMAIN, const.DEVICE_KEY)},
        name=const.NAME,
        model=const.NAME,
        sw_version=const.VERSION,
        manufacturer=const.MANUFACTURER,
    )

    hass.data[const.DOMAIN] = {
        "add_entities": None,
        "entry_id": entry.entry_id,
        "device_id": device.id,
        "store": task_store,
        "entities": {},
    }

    await hass.config_entries.async_forward_entry_setups(entry, [PLATFORM])
    await async_register_panel(hass, entry)

    hass.data[const.DOMAIN]["unsub_tag_scanned"] = hass.bus.async_listen(
        EVENT_TAG_SCANNED, handle_tag_scanned_event
    )
    hass.data[const.DOMAIN]["unsub_state_changed"] = hass.bus.async_listen(
        EVENT_STATE_CHANGED, handle_state_changed
    )
    hass.data[const.DOMAIN]["unsub_notifications"] = async_track_time_change(
        hass, check_notifications, hour=9, minute=0, second=0
    )
    check_notifications()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the Home Maintenance config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, [PLATFORM])
    if not unload_ok:
        return False
    domain_data = hass.data.get(const.DOMAIN, {})
    for key in ("unsub_tag_scanned", "unsub_state_changed", "unsub_notifications"):
        unsub = domain_data.get(key)
        if unsub:
            unsub()
    async_unregister_panel(hass)
    hass.data.pop(const.DOMAIN, None)
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_remove_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,  # noqa: ARG001
) -> None:
    """Clean up when the config entry is removed."""
    async_unregister_panel(hass)
    hass.data.pop(const.DOMAIN, None)


async def async_migrate_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: ConfigEntry,  # noqa: ARG001
) -> bool:
    """Handle migration of config entry data."""
    return True


def _store(hass: HomeAssistant) -> TaskStore | None:
    """Return the loaded task store."""
    data = hass.data.get(const.DOMAIN)
    return data.get("store") if data else None


def _task_id_from_entity(hass: HomeAssistant, entity_id: str) -> str:
    """Resolve a Home Maintenance entity to its task unique ID."""
    registry_entry = er.async_get(hass).async_get(entity_id)
    if registry_entry is None or registry_entry.platform != const.DOMAIN:
        msg = f"Entity {entity_id} is not a Home Maintenance task"
        raise HomeAssistantError(msg)
    return cast("RegistryEntry", registry_entry).unique_id


@callback
def register_services(hass: HomeAssistant) -> None:
    """Register services exposed by Home Maintenance."""

    def require_store() -> TaskStore:
        """Return the task store or raise a user-facing service error."""
        store = _store(hass)
        if store is None:
            msg = "Home Maintenance is not loaded"
            raise HomeAssistantError(msg)
        return store

    async def async_srv_reset(call: ServiceCall) -> None:
        """Complete a task using an optional historical date."""
        performed_date = None
        if value := call.data.get("performed_date"):
            parsed = dt_util.parse_date(value)
            if parsed is None:
                msg = f"Could not parse performed_date: {value}"
                raise HomeAssistantError(msg)
            combined = datetime.combine(parsed, datetime.min.time())
            performed_date = dt_util.as_local(combined)
        require_store().complete_task(
            _task_id_from_entity(hass, call.data["entity_id"]), performed_date
        )

    async def async_srv_create(call: ServiceCall) -> None:
        """Create a recurring task."""
        now = dt_util.now().replace(hour=0, minute=0, second=0, microsecond=0)
        task = HomeMaintenanceTask(
            id=f"home_maintenance_{uuid.uuid4().hex}",
            title=call.data["title"].strip(),
            interval_value=call.data["interval_value"],
            interval_type=call.data["interval_type"],
            last_performed=now.isoformat(),
            description=call.data.get("description") or None,
            url=call.data.get("url") or None,
            icon=call.data.get("icon") or "mdi:calendar-check",
        )
        require_store().add(task)

    async def async_srv_complete(call: ServiceCall) -> None:
        """Complete a task now."""
        task_id = _task_id_from_entity(hass, call.data["entity_id"])
        require_store().complete_task(task_id)

    async def async_srv_snooze(call: ServiceCall) -> None:
        """Snooze a task for the requested number of days."""
        require_store().snooze_task(
            _task_id_from_entity(hass, call.data["entity_id"]), call.data["days"]
        )

    async def async_srv_skip(call: ServiceCall) -> None:
        """Skip the current task occurrence."""
        task_id = _task_id_from_entity(hass, call.data["entity_id"])
        require_store().skip_task(task_id)

    async def async_srv_delete(call: ServiceCall) -> None:
        """Delete a task."""
        task_id = _task_id_from_entity(hass, call.data["entity_id"])
        require_store().delete(task_id)

    services = (
        (const.SERVICE_RESET, async_srv_reset, const.SERVICE_RESET_SCHEMA),
        (const.SERVICE_CREATE, async_srv_create, const.SERVICE_CREATE_SCHEMA),
        (const.SERVICE_COMPLETE, async_srv_complete, const.SERVICE_ENTITY_SCHEMA),
        (const.SERVICE_SNOOZE, async_srv_snooze, const.SERVICE_SNOOZE_SCHEMA),
        (const.SERVICE_SKIP, async_srv_skip, const.SERVICE_ENTITY_SCHEMA),
        (const.SERVICE_DELETE, async_srv_delete, const.SERVICE_ENTITY_SCHEMA),
    )
    for name, handler, schema in services:
        hass.services.async_register(const.DOMAIN, name, handler, schema=schema)
