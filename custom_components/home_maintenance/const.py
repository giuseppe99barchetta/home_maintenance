"""Constants for the Home Maintenance integration."""

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import config_validation as cv

from .schedule import PRIORITIES, SCHEDULE_MODES

VERSION = "2.1.0"
NAME = "Home Maintenance"
MANUFACTURER = "Giuseppe Barchetta"

DOMAIN = "home_maintenance"
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PANEL_FILENAME = "panel/main.js"
PANEL_URL = "home-maintenance"
PANEL_API_PATH = "/home_maintenance_static"
PANEL_API_URL = PANEL_API_PATH + "/main.js"
PANEL_TITLE = NAME
PANEL_ICON = "mdi:hammer-wrench"
PANEL_NAME = "home-maintenance-panel"
DEVICE_KEY = "home_maintenance_hub"

EVENT_TASK_COMPLETED = f"{DOMAIN}_task_completed"
EVENT_TASK_SKIPPED = f"{DOMAIN}_task_skipped"
EVENT_TASK_DUE = f"{DOMAIN}_task_due"

SERVICE_RESET = "reset_last_performed"
SERVICE_CREATE = "create_task"
SERVICE_COMPLETE = "complete_task"
SERVICE_SNOOZE = "snooze_task"
SERVICE_SKIP = "skip_task"
SERVICE_DELETE = "delete_task"
SERVICE_SET_OPTIONS = "set_task_options"

TASK_OPTION_FIELDS = {
    vol.Optional("priority"): vol.In(PRIORITIES),
    vol.Optional("duration_minutes"): vol.Any(
        None, vol.All(vol.Coerce(int), vol.Range(min=0, max=1440))
    ),
    vol.Optional("schedule_mode"): vol.In(SCHEDULE_MODES),
    vol.Optional("active_months"): [vol.All(vol.Coerce(int), vol.Range(min=1, max=12))],
}

SERVICE_RESET_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
        vol.Optional("performed_date"): cv.string,
    }
)

SERVICE_CREATE_SCHEMA = vol.Schema(
    {
        vol.Required("title"): cv.string,
        vol.Required("interval_value"): vol.All(int, vol.Range(min=1)),
        vol.Required("interval_type"): vol.In(("days", "weeks", "months", "years")),
        vol.Optional("description"): cv.string,
        vol.Optional("url"): cv.string,
        vol.Optional("icon"): cv.icon,
        **TASK_OPTION_FIELDS,
    }
)

SERVICE_ENTITY_SCHEMA = vol.Schema({vol.Required("entity_id"): cv.entity_id})


def _require_snooze_length(value: dict) -> dict:
    """Reject snoozes of zero days and zero hours."""
    if value["days"] + value["hours"] < 1:
        msg = "Set at least one day or one hour"
        raise vol.Invalid(msg)
    return value


SERVICE_SNOOZE_SCHEMA = vol.All(
    vol.Schema(
        {
            vol.Required("entity_id"): cv.entity_id,
            vol.Optional("days", default=0): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=3650)
            ),
            vol.Optional("hours", default=0): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=720)
            ),
        }
    ),
    _require_snooze_length,
)
SERVICE_SET_OPTIONS_SCHEMA = vol.Schema(
    {vol.Required("entity_id"): cv.entity_id, **TASK_OPTION_FIELDS}
)

CONFIG_STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional("admin_only", default=True): cv.boolean,
        vol.Optional("sidebar_title", default=PANEL_TITLE): cv.string,
    }
)


def get_options_schema(config_entry: ConfigEntry) -> vol.Schema:
    """Return the schema for get options."""
    return vol.Schema(
        {
            vol.Optional(
                "admin_only",
                default=config_entry.options.get(
                    "admin_only", config_entry.data.get("admin_only", True)
                ),
            ): cv.boolean,
            vol.Optional(
                "sidebar_title",
                default=config_entry.options.get(
                    "sidebar_title",
                    config_entry.data.get("sidebar_title", PANEL_TITLE),
                ),
            ): cv.string,
        }
    )
