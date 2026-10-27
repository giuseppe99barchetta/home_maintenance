"""End-to-end tests for priorities, schedules, seasons and the next-task sensor."""

from datetime import timedelta
from unittest.mock import patch

import pytest

pytest.importorskip("pytest_homeassistant_custom_component")

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
)
from voluptuous import Invalid

import custom_components.home_maintenance  # noqa: F401

DOMAIN = "home_maintenance"
NEXT = "sensor.home_maintenance_next_task"


@pytest.fixture(autouse=True)
def _enable(enable_custom_integrations: None) -> None:
    """Allow loading custom_components."""


async def _setup(hass: HomeAssistant) -> None:
    assert await async_setup_component(hass, "homeassistant", {})
    # The panel needs the real frontend, which is not installed in tests.
    hass.config.components.update({"frontend", "panel_custom"})
    entry = MockConfigEntry(domain=DOMAIN, data={"admin_only": True})
    entry.add_to_hass(hass)
    with (
        patch("custom_components.home_maintenance.async_register_panel"),
        patch("custom_components.home_maintenance.async_unregister_panel"),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()


def _task_entities(hass: HomeAssistant) -> dict[str, str]:
    registry = er.async_get(hass)
    return {
        hass.states.get(e.entity_id).name: e.entity_id
        for e in registry.entities.values()
        if e.platform == DOMAIN and e.domain == "binary_sensor"
    }


async def _refresh(hass: HomeAssistant, *entity_ids: str) -> None:
    await hass.services.async_call(
        "homeassistant",
        "update_entity",
        {"entity_id": list(entity_ids)},
        blocking=True,
    )


async def _call(hass: HomeAssistant, service: str, data: dict) -> None:
    await hass.services.async_call(DOMAIN, service, data, blocking=True)
    await hass.async_block_till_done()


async def test_priorities_queue_snooze_and_fixed_rhythm(hass: HomeAssistant) -> None:
    await _setup(hass)
    assert hass.states.get(NEXT) is not None

    for title, priority, minutes in (("Litter", "high", 10), ("Windows", "low", 45)):
        await _call(
            hass,
            "create_task",
            {
                "title": title,
                "interval_value": 1,
                "interval_type": "weeks",
                "priority": priority,
                "duration_minutes": minutes,
            },
        )
    tasks = _task_entities(hass)
    litter, windows = tasks["Litter"], tasks["Windows"]
    ten_days_ago = (dt_util.now() - timedelta(days=10)).date().isoformat()
    for entity_id in (litter, windows):
        await _call(
            hass,
            "reset_last_performed",
            {"entity_id": entity_id, "performed_date": ten_days_ago},
        )

    state = hass.states.get(litter)
    assert state.state == "on"
    assert state.attributes["priority"] == "high"
    assert state.attributes["duration_minutes"] == 10
    assert state.attributes["priority_score"] == 115

    await _refresh(hass, NEXT)
    nxt = hass.states.get(NEXT)
    assert nxt.state == "Litter"
    assert nxt.attributes["entity_id"] == litter
    assert [item["title"] for item in nxt.attributes["queue"]] == ["Litter", "Windows"]
    assert nxt.attributes["due_count"] == 2

    # Hour snooze hides the task right away.
    await _call(hass, "snooze_task", {"entity_id": litter, "hours": 2})
    await _refresh(hass, litter, NEXT)
    assert hass.states.get(litter).state == "off"
    assert hass.states.get(NEXT).state == "Windows"

    with pytest.raises((HomeAssistantError, Invalid)):
        await _call(hass, "snooze_task", {"entity_id": litter})

    # Seasons and fixed rhythm via set_task_options.
    await _call(
        hass,
        "set_task_options",
        {"entity_id": windows, "schedule_mode": "fixed", "active_months": ["3", "4"]},
    )
    await _refresh(hass, windows)
    attrs = hass.states.get(windows).attributes
    assert attrs["schedule_mode"] == "fixed"
    assert attrs["active_months"] == [3, 4]
    expected = "on" if dt_util.now().month in (3, 4) else "off"
    assert hass.states.get(windows).state == expected

    await _call(hass, "set_task_options", {"entity_id": windows, "active_months": []})
    await _call(hass, "complete_task", {"entity_id": windows})
    await _refresh(hass, windows)
    next_due = dt_util.parse_datetime(
        hass.states.get(windows).attributes["next_due"]
    ).date()
    original_due = (dt_util.now() - timedelta(days=3)).date()
    assert (next_due - original_due).days % 7 == 0
    assert next_due > dt_util.now().date()
    assert hass.states.get(windows).state == "off"


async def test_legacy_storage_gets_defaults(
    hass: HomeAssistant, hass_storage: dict
) -> None:
    hass_storage["home_maintenance.storage"] = {
        "version": 1,
        "minor_version": 2,
        "key": "home_maintenance.storage",
        "data": [
            {
                "id": "home_maintenance_legacy",
                "title": "Legacy",
                "interval_value": 1,
                "interval_type": "weeks",
                "last_performed": "2026-01-01T00:00:00+01:00",
                "history": [],
                "skipped": [],
            }
        ],
    }
    await _setup(hass)
    attrs = hass.states.get(_task_entities(hass)["Legacy"]).attributes
    assert attrs["priority"] == "normal"
    assert attrs["schedule_mode"] == "interval"
    assert attrs["active_months"] == []
