"""Support for Home Maintenance."""

import logging
from datetime import datetime
from typing import cast

from homeassistant.components.binary_sensor import DOMAIN as PLATFORM
from homeassistant.components.tag.const import EVENT_TAG_SCANNED
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_registry import RegistryEntry  # noqa: TC002
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import dt as dt_util

from . import const
from .panel import async_register_panel, async_unregister_panel
from .store import TaskStore
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
        """Mark tasks associated with a scanned tag as performed."""
        tag_id = event.data.get("tag_id")
        domain_data = hass.data.get(const.DOMAIN)
        store = domain_data.get("store") if domain_data else None
        if store is None or not tag_id:
            return

        tasks = store.get_by_tag_uuid(tag_id)
        if not tasks:
            return

        _LOGGER.debug("Tag scanned: %s", tag_id)
        for task in tasks:
            store.update_last_performed(task["id"])

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

    unsub = hass.bus.async_listen(EVENT_TAG_SCANNED, handle_tag_scanned_event)
    hass.data[const.DOMAIN]["unsub_tag_scanned"] = unsub

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the Home Maintenance config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, [PLATFORM])
    if not unload_ok:
        return False

    domain_data = hass.data.get(const.DOMAIN, {})
    unsub = domain_data.get("unsub_tag_scanned")
    if unsub:
        unsub()

    async_unregister_panel(hass)
    hass.data.pop(const.DOMAIN, None)
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:  # noqa: ARG001
    """Clean up when the config entry is removed."""
    async_unregister_panel(hass)
    hass.data.pop(const.DOMAIN, None)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:  # noqa: ARG001
    """Handle migration of config entry data."""
    return True


@callback
def register_services(hass: HomeAssistant) -> None:
    """Register services exposed by Home Maintenance."""

    async def async_srv_reset(call: ServiceCall) -> None:
        entity_id = call.data["entity_id"]
        performed_date_str = call.data.get("performed_date")

        performed_date = None
        if performed_date_str is not None:
            parsed_date = dt_util.parse_date(performed_date_str)
            if parsed_date is None:
                msg = f"Could not parse performed_date: {performed_date_str}"
                raise HomeAssistantError(msg)
            combined_date = datetime.combine(parsed_date, datetime.min.time())
            performed_date = dt_util.as_local(combined_date)

        domain_data = hass.data.get(const.DOMAIN)
        if not domain_data:
            msg = "Home Maintenance is not loaded"
            raise HomeAssistantError(msg)

        entity_registry = er.async_get(hass)
        registry_entry = entity_registry.async_get(entity_id)
        if registry_entry is None or registry_entry.platform != const.DOMAIN:
            msg = f"Entity {entity_id} is not a Home Maintenance task"
            raise HomeAssistantError(msg)

        entry = cast("RegistryEntry", registry_entry)
        task_id = entry.unique_id
        entity = domain_data["entities"].get(task_id)
        if entity is None:
            msg = f"Task entity {entity_id} is not loaded"
            raise HomeAssistantError(msg)

        store = domain_data.get("store")
        if store is None:
            msg = "Home Maintenance task store is not loaded"
            raise HomeAssistantError(msg)
        store.update_last_performed(task_id, performed_date)

    hass.services.async_register(
        const.DOMAIN,
        const.SERVICE_RESET,
        async_srv_reset,
        schema=const.SERVICE_RESET_SCHEMA,
    )
