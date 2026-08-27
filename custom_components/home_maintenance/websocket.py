"""WebSocket commands for the Home Maintenance integration."""

import uuid
from collections.abc import Callable
from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.components.websocket_api import connection, messages
from homeassistant.core import HomeAssistant, callback
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .schedule import INTERVAL_TYPES
from .store import HomeMaintenanceTask, TaskStore

PRESETS = [
    {
        "title": "Clean HVAC filter",
        "interval_value": 3,
        "interval_type": "months",
        "icon": "mdi:air-filter",
    },
    {
        "title": "Descale coffee machine",
        "interval_value": 2,
        "interval_type": "months",
        "icon": "mdi:coffee-maker",
    },
    {
        "title": "Check smoke detector",
        "interval_value": 6,
        "interval_type": "months",
        "icon": "mdi:smoke-detector",
    },
    {
        "title": "Replace water filter",
        "interval_value": 6,
        "interval_type": "months",
        "icon": "mdi:water",
    },
    {
        "title": "Service boiler",
        "interval_value": 1,
        "interval_type": "years",
        "icon": "mdi:water-boiler",
    },
]

TASK_UPDATES_SCHEMA = vol.Schema(
    {
        vol.Optional("title"): vol.All(str, vol.Length(min=1, max=120)),
        vol.Optional("interval_value"): vol.All(int, vol.Range(min=1)),
        vol.Optional("interval_type"): vol.In(INTERVAL_TYPES),
        vol.Optional("last_performed"): str,
        vol.Optional("tag_id"): vol.Any(str, None),
        vol.Optional("icon"): vol.Any(str, None),
        vol.Optional("labels"): [str],
        vol.Optional("description"): vol.Any(str, None),
        vol.Optional("url"): vol.Any(str, None),
        vol.Optional("notify_enabled"): bool,
        vol.Optional("notify_before_days"): vol.All(int, vol.Range(min=0, max=365)),
        vol.Optional("source_entity_id"): vol.Any(str, None),
        vol.Optional("source_state"): vol.Any(str, None),
    },
    extra=vol.PREVENT_EXTRA,
)

WebsocketHandler = Callable[
    [HomeAssistant, connection.ActiveConnection, dict[str, Any]], None
]


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
    """Normalize a frontend date or datetime to local midnight."""
    if not value:
        return (
            dt_util.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        )
    parsed = dt_util.parse_datetime(value)
    if parsed is None:
        return None
    return (
        dt_util.as_local(parsed)
        .replace(hour=0, minute=0, second=0, microsecond=0)
        .isoformat()
    )


def _send_success(
    conn: connection.ActiveConnection,
    msg: dict[str, Any],
    value: Any | None = None,
) -> None:
    """Send a standard successful WebSocket response."""
    conn.send_result(msg["id"], {"success": True} if value is None else value)


@callback
def websocket_get_tasks(
    hass: HomeAssistant,
    conn: connection.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return all maintenance tasks."""
    store = _get_store(hass, conn, msg)
    if store is not None:
        conn.send_result(msg["id"], store.get_all())


@callback
def websocket_get_task(
    hass: HomeAssistant,
    conn: connection.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return one maintenance task."""
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
    hass: HomeAssistant,
    conn: connection.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Create a maintenance task."""
    store = _get_store(hass, conn, msg)
    if store is None:
        return

    title = msg["title"].strip()
    if not title:
        conn.send_error(msg["id"], "invalid_title", "Task title cannot be empty")
        return

    last_performed = _normalize_date(msg.get("last_performed"))
    if last_performed is None:
        conn.send_error(msg["id"], "invalid_date", "Could not parse last_performed")
        return

    task = HomeMaintenanceTask(
        id=f"home_maintenance_{uuid.uuid4().hex}",
        title=title,
        interval_value=msg["interval_value"],
        interval_type=msg["interval_type"],
        last_performed=last_performed,
        tag_id=msg.get("tag_id") or None,
        icon=msg.get("icon") or "mdi:calendar-check",
        description=msg.get("description") or None,
        url=msg.get("url") or None,
        notify_enabled=msg.get("notify_enabled", False),
        notify_before_days=msg.get("notify_before_days", 0),
        source_entity_id=msg.get("source_entity_id") or None,
        source_state=msg.get("source_state") or None,
    )
    try:
        new_id = store.add(task, msg.get("labels", []))
    except RuntimeError as err:
        conn.send_error(msg["id"], "add_failed", str(err))
        return
    _send_success(conn, msg, {"success": True, "id": new_id})


@callback
def websocket_update_task(
    hass: HomeAssistant,
    conn: connection.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Update an existing maintenance task."""
    store = _get_store(hass, conn, msg)
    if store is None:
        return
    if store.get(msg["task_id"]) is None:
        conn.send_error(msg["id"], "not_found", "Task not found")
        return

    updates = dict(msg["updates"])
    if "title" in updates:
        updates["title"] = updates["title"].strip()
        if not updates["title"]:
            conn.send_error(msg["id"], "invalid_title", "Task title cannot be empty")
            return

    if "last_performed" in updates:
        normalized = _normalize_date(updates["last_performed"])
        if normalized is None:
            conn.send_error(msg["id"], "invalid_date", "Could not parse last_performed")
            return
        updates["last_performed"] = normalized

    try:
        store.update_task(msg["task_id"], updates)
    except RuntimeError as err:
        conn.send_error(msg["id"], "update_failed", str(err))
        return
    _send_success(conn, msg)


@callback
def websocket_complete_task(
    hass: HomeAssistant,
    conn: connection.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Complete a maintenance task now."""
    store = _get_store(hass, conn, msg)
    if store is None:
        return
    try:
        store.complete_task(msg["task_id"])
    except RuntimeError as err:
        conn.send_error(msg["id"], "complete_failed", str(err))
        return
    _send_success(conn, msg)


@callback
def websocket_snooze_task(
    hass: HomeAssistant,
    conn: connection.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Snooze a maintenance task."""
    store = _get_store(hass, conn, msg)
    if store is None:
        return
    try:
        store.snooze_task(msg["task_id"], msg["days"])
    except RuntimeError as err:
        conn.send_error(msg["id"], "snooze_failed", str(err))
        return
    _send_success(conn, msg)


@callback
def websocket_skip_task(
    hass: HomeAssistant,
    conn: connection.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Skip the current maintenance occurrence."""
    store = _get_store(hass, conn, msg)
    if store is None:
        return
    try:
        store.skip_task(msg["task_id"])
    except RuntimeError as err:
        conn.send_error(msg["id"], "skip_failed", str(err))
        return
    _send_success(conn, msg)


@callback
def websocket_remove_task(
    hass: HomeAssistant,
    conn: connection.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Delete a maintenance task."""
    store = _get_store(hass, conn, msg)
    if store is None:
        return
    try:
        store.delete(msg["task_id"])
    except RuntimeError as err:
        conn.send_error(msg["id"], "remove_failed", str(err))
        return
    _send_success(conn, msg)


@callback
def websocket_statistics(
    hass: HomeAssistant,
    conn: connection.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return aggregate maintenance statistics."""
    store = _get_store(hass, conn, msg)
    if store is not None:
        conn.send_result(msg["id"], store.statistics())


@callback
def websocket_export(
    hass: HomeAssistant,
    conn: connection.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Export portable maintenance task data."""
    store = _get_store(hass, conn, msg)
    if store is not None:
        conn.send_result(msg["id"], {"version": 2, "tasks": store.export_data()})


@callback
def websocket_import(
    hass: HomeAssistant,
    conn: connection.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Import portable maintenance task data."""
    store = _get_store(hass, conn, msg)
    if store is None:
        return
    try:
        count = store.import_data(msg["tasks"])
    except (RuntimeError, TypeError, ValueError) as err:
        conn.send_error(msg["id"], "import_failed", str(err))
        return
    _send_success(conn, msg, {"success": True, "imported": count})


@callback
def websocket_presets(
    hass: HomeAssistant,  # noqa: ARG001
    conn: connection.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return built-in maintenance task presets."""
    conn.send_result(msg["id"], PRESETS)


@callback
def websocket_get_config(
    hass: HomeAssistant,
    conn: connection.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return integration configuration relevant to the panel."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        conn.send_error(
            msg["id"],
            "not_found",
            "No Home Maintenance config entry found",
        )
        return
    entry = entries[0]
    conn.send_result(
        msg["id"],
        {"data": dict(entry.data), "options": dict(entry.options)},
    )


def _register_command(
    hass: HomeAssistant,
    name: str,
    handler: WebsocketHandler,
    extra_schema: dict[Any, Any] | None = None,
) -> None:
    """Register one Home Maintenance WebSocket command."""
    schema = {
        vol.Required("type"): f"{DOMAIN}/{name}",
        **(extra_schema or {}),
    }
    websocket_api.async_register_command(
        hass,
        f"{DOMAIN}/{name}",
        handler,
        messages.BASE_COMMAND_MESSAGE_SCHEMA.extend(schema),
    )


async def async_register_websockets(hass: HomeAssistant) -> None:
    """Register Home Maintenance WebSocket commands."""
    _register_command(hass, "get_tasks", websocket_get_tasks)
    _register_command(
        hass,
        "get_task",
        websocket_get_task,
        {vol.Required("task_id"): str},
    )
    _register_command(
        hass,
        "complete_task",
        websocket_complete_task,
        {vol.Required("task_id"): str},
    )
    _register_command(
        hass,
        "skip_task",
        websocket_skip_task,
        {vol.Required("task_id"): str},
    )
    _register_command(
        hass,
        "remove_task",
        websocket_remove_task,
        {vol.Required("task_id"): str},
    )
    _register_command(
        hass,
        "snooze_task",
        websocket_snooze_task,
        {
            vol.Required("task_id"): str,
            vol.Required("days"): vol.All(int, vol.Range(min=1, max=3650)),
        },
    )
    _register_command(hass, "statistics", websocket_statistics)
    _register_command(hass, "export", websocket_export)
    _register_command(hass, "presets", websocket_presets)
    _register_command(hass, "get_config", websocket_get_config)

    add_schema = {
        vol.Required("title"): vol.All(str, vol.Length(min=1, max=120)),
        vol.Required("interval_value"): vol.All(int, vol.Range(min=1)),
        vol.Required("interval_type"): vol.In(INTERVAL_TYPES),
        vol.Optional("last_performed"): str,
        vol.Optional("tag_id"): str,
        vol.Optional("icon"): str,
        vol.Optional("labels"): [str],
        vol.Optional("description"): str,
        vol.Optional("url"): str,
        vol.Optional("notify_enabled"): bool,
        vol.Optional("notify_before_days"): vol.All(int, vol.Range(min=0, max=365)),
        vol.Optional("source_entity_id"): str,
        vol.Optional("source_state"): str,
    }
    _register_command(hass, "add_task", websocket_add_task, add_schema)
    _register_command(
        hass,
        "update_task",
        websocket_update_task,
        {
            vol.Required("task_id"): str,
            vol.Required("updates"): TASK_UPDATES_SCHEMA,
        },
    )
    _register_command(
        hass,
        "import",
        websocket_import,
        {vol.Required("tasks"): [dict]},
    )
