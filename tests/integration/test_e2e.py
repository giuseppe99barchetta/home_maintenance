"""End-to-end tests for priorities, schedules, seasons and the next-task sensor."""

from datetime import datetime, timedelta
from typing import Any
from unittest.mock import patch

import pytest

pytest.importorskip("pytest_homeassistant_custom_component")

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
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


async def test_fixed_monthly_rhythm_survives_successive_completions(
    hass: HomeAssistant,
) -> None:
    await _setup(hass)
    await _call(
        hass,
        "create_task",
        {"title": "Month end", "interval_value": 1, "interval_type": "months"},
    )
    entity_id = _task_entities(hass)["Month end"]
    store = hass.data[DOMAIN]["store"]
    task_id = er.async_get(hass).async_get(entity_id).unique_id
    tz = dt_util.get_default_time_zone()
    store.update_task(
        task_id,
        {"last_performed": "2025-12-31T00:00:00+01:00", "schedule_mode": "fixed"},
    )

    seen = []
    for day in ("2026-01-31", "2026-02-28", "2026-03-31"):
        done = datetime.fromisoformat(day).replace(tzinfo=tz)
        store.complete_task(task_id, done)
        seen.append(store.get(task_id)["next_due_override"][:10])
    assert seen == ["2026-02-28", "2026-03-31", "2026-04-30"]
    assert store.get(task_id)["schedule_anchor"][:10] == "2026-01-31"

    # Changing the interval starts a new series.
    store.update_task(task_id, {"interval_value": 2})
    assert store.get(task_id)["schedule_anchor"] is None


async def test_checklist_steps_autocomplete_and_reset(
    hass: HomeAssistant, hass_storage: dict
) -> None:
    await _setup(hass)
    await _call(
        hass,
        "create_task",
        {
            "title": "Bathroom",
            "interval_value": 1,
            "interval_type": "weeks",
            "checklist": ["Sanitari", "Specchio", "Pavimento"],
        },
    )
    entity_id = _task_entities(hass)["Bathroom"]
    await _call(hass, "check_step", {"entity_id": entity_id, "step": 1})
    await _call(hass, "check_step", {"entity_id": entity_id, "step": "specchio"})
    await _refresh(hass, entity_id)
    attrs = hass.states.get(entity_id).attributes
    assert attrs["checklist"] == ["Sanitari", "Specchio", "Pavimento"]
    assert attrs["checklist_done"] == ["Sanitari", "Specchio"]
    assert attrs["checklist_progress"] == "2/3"

    # Toggling twice is a no-op; unchecking works.
    await _call(hass, "check_step", {"entity_id": entity_id, "step": 2})
    await _call(hass, "check_step", {"entity_id": entity_id, "step": 2})
    await _call(
        hass, "check_step", {"entity_id": entity_id, "step": 1, "checked": False}
    )
    await _refresh(hass, entity_id)
    assert hass.states.get(entity_id).attributes["checklist_progress"] == "1/3"

    # Progress is persisted.
    await hass.async_block_till_done()
    saved = next(
        t
        for t in hass_storage["home_maintenance.storage"]["data"]
        if t["title"] == "Bathroom"
    )
    assert saved["checklist_done"] == [1]

    with pytest.raises(HomeAssistantError):
        await _call(hass, "check_step", {"entity_id": entity_id, "step": "nope"})

    completed = []
    hass.bus.async_listen(
        "home_maintenance_task_completed", lambda e: completed.append(e.data)
    )
    for step in (1, 3):
        await _call(hass, "check_step", {"entity_id": entity_id, "step": step})
    await hass.async_block_till_done()
    assert completed[-1]["source"] == "checklist"
    await _refresh(hass, entity_id)
    attrs = hass.states.get(entity_id).attributes
    assert attrs["checklist_done"] == []
    assert attrs["history_count"] == 1

    # Changing the steps resets progress; disabling auto-complete is honoured.
    await _call(hass, "check_step", {"entity_id": entity_id, "step": 1})
    await _call(
        hass,
        "set_task_options",
        {
            "entity_id": entity_id,
            "checklist": ["Solo pavimento"],
            "checklist_autocomplete": False,
        },
    )
    await _call(hass, "check_step", {"entity_id": entity_id, "step": 1})
    await _refresh(hass, entity_id)
    attrs = hass.states.get(entity_id).attributes
    assert attrs["checklist_progress"] == "1/1"
    assert attrs["history_count"] == 1


async def test_streak_sensor_and_statistics(
    hass: HomeAssistant, hass_storage: dict
) -> None:
    today = dt_util.now().date()
    monday = today - timedelta(days=today.weekday())
    weeks = [monday - timedelta(weeks=n) for n in (4, 3, 2, 1)]
    history = [f"{d.isoformat()}T00:00:00+00:00" for d in weeks]
    hass_storage["home_maintenance.storage"] = {
        "version": 1,
        "minor_version": 2,
        "key": "home_maintenance.storage",
        "data": [
            {
                "id": "home_maintenance_litter",
                "title": "Litter",
                "interval_value": 1,
                "interval_type": "weeks",
                "last_performed": history[-1],
                "history": history,
                "skipped": [],
                "priority": "high",
            }
        ],
    }
    await _setup(hass)
    await _refresh(hass, "sensor.home_maintenance_streak")
    state = hass.states.get("sensor.home_maintenance_streak")
    # Four completed weeks in a row; this week's occurrence is still open.
    assert int(state.state) == 4
    assert state.attributes["best"] == 4
    assert state.attributes["current_week_ok"] is False
    assert state.attributes["tracked_tasks"] == 1
    assert hass.data[DOMAIN]["store"].statistics()["streak"]["current"] == 4


async def test_ai_suggestions_go_through_ai_task(
    hass: HomeAssistant, hass_ws_client: Any
) -> None:
    await _setup(hass)
    client = await hass_ws_client(hass)

    await client.send_json({"id": 1, "type": "home_maintenance/ai_status"})
    status = (await client.receive_json())["result"]
    assert status == {"available": False, "entities": [], "entity_id": None}

    await client.send_json(
        {"id": 2, "type": "home_maintenance/ai_suggest_task", "description": "x"}
    )
    assert (await client.receive_json())["error"]["code"] == "ai_failed"

    calls: list[dict] = []

    async def generate(call: ServiceCall) -> dict:
        calls.append(dict(call.data))
        if "checklist suggestion" in call.data["task_name"]:
            return {"data": {"checklist": ["Smonta", "Lava", "Rimonta"]}}
        return {
            "data": {
                "title": "Filtro lavastoviglie",
                "interval_value": 1,
                "interval_type": "months",
                "priority": "normal",
                "icon": "mdi:dishwasher",
                "checklist": ["Smonta", "Lava"],
            }
        }

    hass.services.async_register(
        "ai_task", "generate_data", generate, supports_response=SupportsResponse.ONLY
    )
    hass.states.async_set("ai_task.fake", "unknown", {"friendly_name": "Fake AI"})

    await client.send_json({"id": 3, "type": "home_maintenance/ai_status"})
    status = (await client.receive_json())["result"]
    assert status["available"] is True
    assert status["entities"] == [{"entity_id": "ai_task.fake", "name": "Fake AI"}]

    await client.send_json(
        {
            "id": 4,
            "type": "home_maintenance/ai_suggest_task",
            "description": "pulire il filtro della lavastoviglie",
        }
    )
    proposal = (await client.receive_json())["result"]
    assert proposal["title"] == "Filtro lavastoviglie"
    assert proposal["checklist"] == ["Smonta", "Lava"]
    assert "pulire il filtro della lavastoviglie" in calls[-1]["instructions"]
    assert "entity_id" not in calls[-1]  # Home Assistant's default AI Task

    # With an AI Task chosen in the options, it is passed explicitly.
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "ai_task_entity": "ai_task.fake"}
    )
    await client.send_json(
        {
            "id": 5,
            "type": "home_maintenance/ai_suggest_steps",
            "title": "Pulizia bagno",
        }
    )
    assert (await client.receive_json())["result"] == {
        "checklist": ["Smonta", "Lava", "Rimonta"]
    }
    assert calls[-1]["entity_id"] == "ai_task.fake"
    # Suggestions never create anything by themselves.
    assert _task_entities(hass) == {}
