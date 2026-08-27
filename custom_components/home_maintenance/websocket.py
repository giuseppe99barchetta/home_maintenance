"""WebSocket commands for the Home Maintenance integration."""

import uuid
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
    {"title": "Clean HVAC filter", "interval_value": 3, "interval_type": "months", "icon": "mdi:air-filter"},
    {"title": "Descale coffee machine", "interval_value": 2, "interval_type": "months", "icon": "mdi:coffee-maker"},
    {"title": "Check smoke detector", "interval_value": 6, "interval_type": "months", "icon": "mdi:smoke-detector"},
    {"title": "Replace water filter", "interval_value": 6, "interval_type": "months", "icon": "mdi:water"},
    {"title": "Service boiler", "interval_value": 1, "interval_type": "years", "icon": "mdi:water-boiler"},
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


def _get_store(hass: HomeAssistant, conn: connection.ActiveConnection, msg: dict[str, Any]) -> TaskStore | None:
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
        return dt_util.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    parsed = dt_util.parse_datetime(value)
    if parsed is None:
        return None
    return dt_util.as_local(parsed).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()


def _result(conn: connection.ActiveConnection, msg: dict[str, Any], value: Any = None) -> None:
    conn.send_result(msg["id"], {"success": True} if value is None else value)


@callback
def websocket_get_tasks(hass, conn, msg):
    store = _get_store(hass, conn, msg)
    if store:
        conn.send_result(msg["id"], store.get_all())


@callback
def websocket_get_task(hass, conn, msg):
    store = _get_store(hass, conn, msg)
    if not store:
        return
    task = store.get(msg["task_id"])
    if task is None:
        conn.send_error(msg["id"], "not_found", "Task not found")
        return
    conn.send_result(msg["id"], task)


@callback
def websocket_add_task(hass, conn, msg):
    store = _get_store(hass, conn, msg)
    if not store:
        return
    title = msg["title"].strip()
    if not title:
        conn.send_error(msg["id"], "invalid_title", "Task title cannot be empty")
        return
    last = _normalize_date(msg.get("last_performed"))
    if last is None:
        conn.send_error(msg["id"], "invalid_date", "Could not parse last_performed")
        return
    task = HomeMaintenanceTask(
        id=f"home_maintenance_{uuid.uuid4().hex}",
        title=title,
        interval_value=msg["interval_value"],
        interval_type=msg["interval_type"],
        last_performed=last,
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
    _result(conn, msg, {"success": True, "id": new_id})


@callback
def websocket_update_task(hass, conn, msg):
    store = _get_store(hass, conn, msg)
    if not store:
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
        updates["last_performed"] = _normalize_date(updates["last_performed"])
        if updates["last_performed"] is None:
            conn.send_error(msg["id"], "invalid_date", "Could not parse last_performed")
            return
    try:
        store.update_task(msg["task_id"], updates)
    except RuntimeError as err:
        conn.send_error(msg["id"], "update_failed", str(err))
        return
    _result(conn, msg)


@callback
def websocket_complete_task(hass, conn, msg):
    store = _get_store(hass, conn, msg)
    if not store:
        return
    try:
        store.complete_task(msg["task_id"])
    except RuntimeError as err:
        conn.send_error(msg["id"], "complete_failed", str(err))
        return
    _result(conn, msg)


@callback
def websocket_snooze_task(hass, conn, msg):
    store = _get_store(hass, conn, msg)
    if not store:
        return
    try:
        store.snooze_task(msg["task_id"], msg["days"])
    except RuntimeError as err:
        conn.send_error(msg["id"], "snooze_failed", str(err))
        return
    _result(conn, msg)


@callback
def websocket_skip_task(hass, conn, msg):
    store = _get_store(hass, conn, msg)
    if not store:
        return
    try:
        store.skip_task(msg["task_id"])
    except RuntimeError as err:
        conn.send_error(msg["id"], "skip_failed", str(err))
        return
    _result(conn, msg)


@callback
def websocket_remove_task(hass, conn, msg):
    store = _get_store(hass, conn, msg)
    if not store:
        return
    try:
        store.delete(msg["task_id"])
    except RuntimeError as err:
        conn.send_error(msg["id"], "remove_failed", str(err))
        return
    _result(conn, msg)


@callback
def websocket_statistics(hass, conn, msg):
    store = _get_store(hass, conn, msg)
    if store:
        conn.send_result(msg["id"], store.statistics())


@callback
def websocket_export(hass, conn, msg):
    store = _get_store(hass, conn, msg)
    if store:
        conn.send_result(msg["id"], {"version": 2, "tasks": store.export_data()})


@callback
def websocket_import(hass, conn, msg):
    store = _get_store(hass, conn, msg)
    if not store:
        return
    try:
        count = store.import_data(msg["tasks"])
    except (RuntimeError, TypeError, ValueError) as err:
        conn.send_error(msg["id"], "import_failed", str(err))
        return
    _result(conn, msg, {"success": True, "imported": count})


@callback
def websocket_presets(hass, conn, msg):  # noqa: ARG001
    conn.send_result(msg["id"], PRESETS)


@callback
def websocket_get_config(hass, conn, msg):
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        conn.send_error(msg["id"], "not_found", "No Home Maintenance config entry found")
        return
    entry = entries[0]
    conn.send_result(msg["id"], {"data": dict(entry.data), "options": dict(entry.options)})


async def async_register_websockets(hass: HomeAssistant) -> None:
    """Register Home Maintenance WebSocket commands."""
    specs = [
        ("get_tasks", websocket_get_tasks, {}),
        ("get_task", websocket_get_task, {vol.Required("task_id"): str}),
        ("complete_task", websocket_complete_task, {vol.Required("task_id"): str}),
        ("skip_task", websocket_skip_task, {vol.Required("task_id"): str}),
        ("remove_task", websocket_remove_task, {vol.Required("task_id"): str}),
        ("snooze_task", websocket_snooze_task, {vol.Required("task_id"): str, vol.Required("days"): vol.All(int, vol.Range(min=1, max=3650))}),
        ("statistics", websocket_statistics, {}),
        ("export", websocket_export, {}),
        ("presets", websocket_presets, {}),
        ("get_config", websocket_get_config, {}),
    ]
    for name, handler, extra in specs:
        websocket_api.async_register_command(
            hass,
            f"{DOMAIN}/{name}",
            handler,
            messages.BASE_COMMAND_MESSAGE_SCHEMA.extend({vol.Required("type"): f"{DOMAIN}/{name}", **extra}),
        )

    websocket_api.async_register_command(
        hass,
        f"{DOMAIN}/add_task",
        websocket_add_task,
        messages.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {
                vol.Required("type"): f"{DOMAIN}/add_task",
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
        ),
    )
    websocket_api.async_register_command(
        hass,
        f"{DOMAIN}/update_task",
        websocket_update_task,
        messages.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {
                vol.Required("type"): f"{DOMAIN}/update_task",
                vol.Required("task_id"): str,
                vol.Required("updates"): TASK_UPDATES_SCHEMA,
            }
        ),
    )
    websocket_api.async_register_command(
        hass,
        f"{DOMAIN}/import",
        websocket_import,
        messages.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {vol.Required("type"): f"{DOMAIN}/import", vol.Required("tasks"): [dict]}
        ),
    )
