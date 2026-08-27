"""WebSocket commands for the Home Maintenance integration."""

import uuid
from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.components.websocket_api import connection, messages
from homeassistant.core import HomeAssistant, callback
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .store import HomeMaintenanceTask, TaskStore

INTERVAL_TYPES = ("days", "weeks", "months")

TASK_UPDATES_SCHEMA = vol.Schema(
    {
        vol.Optional("title"): vol.All(str, vol.Length(min=1, max=120)),
        vol.Optional("interval_value"): vol.All(int, vol.Range(min=1)),
        vol.Optional("interval_type"): vol.In(INTERVAL_TYPES),
        vol.Optional("last_performed"): str,
        vol.Optional("tag_id"): vol.Any(str, None),
        vol.Optional("icon"): vol.Any(str, None),
        vol.Optional("labels"): [str],
    },
    extra=vol.PREVENT_EXTRA,
)


def _get_store(
    hass: HomeAssistant,
    conn: connection.ActiveConnection,
    msg: dict[str, Any],
) -> TaskStore | None:
    """Return the task store or send a useful WebSocket error."""
    domain_data = hass.data.get(DOMAIN)
    store = domain_data.get("store") if domain_data else None
    if store is None:
        conn.send_error(msg["id"], "not_loaded", "Home Maintenance is not loaded")
        return None
    return store


def _normalize_date(value: str | None) -> str | None:
    """Normalize a frontend date/datetime to local midnight."""
    if not value:
        return (
            dt_util.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        )

    parsed = dt_util.parse_datetime(value)
    if parsed is None:
        return None

    parsed_local = dt_util.as_local(parsed)
    return parsed_local.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()


@callback
def websocket_get_tasks(
    hass: HomeAssistant, conn: connection.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Return all tasks."""
    store = _get_store(hass, conn, msg)
    if store is None:
        return
    conn.send_result(msg["id"], store.get_all())


@callback
def websocket_get_task(
    hass: HomeAssistant, conn: connection.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Return one task."""
    store = _get_store(hass, conn, msg)
    if store is None:
        return

    task = store.get(msg["task_id"])
    if task is None:
        conn.send_error(msg["id"], "not_found", "Task not found")
        return
    conn.send_result(msg["id"], task)


@callback
def websocket_add_task(
    hass: HomeAssistant, conn: connection.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Add a new task."""
    store = _get_store(hass, conn, msg)
    if store is None:
        return

    title = msg["title"].strip()
    if not title:
        conn.send_error(msg["id"], "invalid_title", "Task title cannot be empty")
        return

    last_performed = _normalize_date(msg.get("last_performed"))
    if last_performed is None:
        conn.send_error(
            msg["id"],
            "invalid_date",
            f"Could not parse date: {msg.get('last_performed')}",
        )
        return

    new_task = HomeMaintenanceTask(
        id=f"home_maintenance_{uuid.uuid4().hex}",
        title=title,
        interval_value=msg["interval_value"],
        interval_type=msg["interval_type"],
        last_performed=last_performed,
        tag_id=(msg.get("tag_id") or None),
        icon=(msg.get("icon") or "mdi:calendar-check"),
    )

    try:
        new_id = store.add(new_task, msg.get("labels", []))
    except RuntimeError as err:
        conn.send_error(msg["id"], "add_failed", str(err))
        return

    conn.send_result(msg["id"], {"success": True, "id": new_id})


@callback
def websocket_update_task(
    hass: HomeAssistant, conn: connection.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Update an existing task."""
    store = _get_store(hass, conn, msg)
    if store is None:
        return

    task_id = msg["task_id"]
    if store.get(task_id) is None:
        conn.send_error(msg["id"], "not_found", "Task not found")
        return

    updates = dict(msg.get("updates", {}))
    if "title" in updates:
        updates["title"] = updates["title"].strip()
        if not updates["title"]:
            conn.send_error(msg["id"], "invalid_title", "Task title cannot be empty")
            return

    if "last_performed" in updates:
        normalized = _normalize_date(updates["last_performed"])
        if normalized is None:
            conn.send_error(
                msg["id"],
                "invalid_date",
                f"Could not parse date: {updates['last_performed']}",
            )
            return
        updates["last_performed"] = normalized

    if "tag_id" in updates:
        updates["tag_id"] = updates["tag_id"] or None
    if "icon" in updates:
        updates["icon"] = updates["icon"] or "mdi:calendar-check"

    try:
        store.update_task(task_id, updates)
    except RuntimeError as err:
        conn.send_error(msg["id"], "update_failed", str(err))
        return

    conn.send_result(msg["id"], {"success": True})


@callback
def websocket_complete_task(
    hass: HomeAssistant, conn: connection.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Mark a task as completed."""
    store = _get_store(hass, conn, msg)
    if store is None:
        return

    try:
        store.update_last_performed(msg["task_id"])
    except RuntimeError as err:
        conn.send_error(msg["id"], "complete_failed", str(err))
        return
    conn.send_result(msg["id"], {"success": True})


@callback
def websocket_remove_task(
    hass: HomeAssistant, conn: connection.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Remove a task."""
    store = _get_store(hass, conn, msg)
    if store is None:
        return

    try:
        store.delete(msg["task_id"])
    except RuntimeError as err:
        conn.send_error(msg["id"], "remove_failed", str(err))
        return
    conn.send_result(msg["id"], {"success": True})


@callback
def websocket_get_config(
    hass: HomeAssistant, conn: connection.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Return integration configuration."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        conn.send_error(
            msg["id"], "not_found", "No Home Maintenance config entry found"
        )
        return

    entry = entries[0]
    conn.send_result(
        msg["id"],
        {
            "data": dict(entry.data),
            "options": dict(entry.options),
        },
    )


async def async_register_websockets(hass: HomeAssistant) -> None:
    """Register Home Maintenance WebSocket commands."""
    websocket_api.async_register_command(
        hass,
        "home_maintenance/get_tasks",
        websocket_get_tasks,
        messages.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {vol.Required("type"): "home_maintenance/get_tasks"}
        ),
    )
    websocket_api.async_register_command(
        hass,
        "home_maintenance/get_task",
        websocket_get_task,
        messages.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {
                vol.Required("type"): "home_maintenance/get_task",
                vol.Required("task_id"): str,
            }
        ),
    )
    websocket_api.async_register_command(
        hass,
        "home_maintenance/add_task",
        websocket_add_task,
        messages.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {
                vol.Required("type"): "home_maintenance/add_task",
                vol.Required("title"): vol.All(str, vol.Length(min=1, max=120)),
                vol.Required("interval_value"): vol.All(int, vol.Range(min=1)),
                vol.Required("interval_type"): vol.In(INTERVAL_TYPES),
                vol.Optional("last_performed"): str,
                vol.Optional("tag_id"): str,
                vol.Optional("icon"): str,
                vol.Optional("labels"): [str],
            }
        ),
    )
    websocket_api.async_register_command(
        hass,
        "home_maintenance/update_task",
        websocket_update_task,
        messages.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {
                vol.Required("type"): "home_maintenance/update_task",
                vol.Required("task_id"): str,
                vol.Required("updates"): TASK_UPDATES_SCHEMA,
            }
        ),
    )
    websocket_api.async_register_command(
        hass,
        "home_maintenance/complete_task",
        websocket_complete_task,
        messages.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {
                vol.Required("type"): "home_maintenance/complete_task",
                vol.Required("task_id"): str,
            }
        ),
    )
    websocket_api.async_register_command(
        hass,
        "home_maintenance/remove_task",
        websocket_remove_task,
        messages.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {
                vol.Required("type"): "home_maintenance/remove_task",
                vol.Required("task_id"): str,
            }
        ),
    )
    websocket_api.async_register_command(
        hass,
        "home_maintenance/get_config",
        websocket_get_config,
        messages.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {vol.Required("type"): "home_maintenance/get_config"}
        ),
    )
