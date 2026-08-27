"""Tests for task storage compatibility."""

from custom_components.home_maintenance.store import HomeMaintenanceTask


def test_old_task_data_gets_v2_defaults() -> None:
    task = HomeMaintenanceTask.from_dict(
        {
            "id": "home_maintenance_old",
            "title": "Old task",
            "interval_value": 1,
            "interval_type": "months",
            "last_performed": "2026-08-01T00:00:00+02:00",
            "tag_id": None,
            "icon": "mdi:hammer",
        }
    )
    assert task.history == []
    assert task.skipped == []
    assert task.snoozed_until is None
    assert task.notify_enabled is False
    assert task.source_entity_id is None


def test_unknown_storage_fields_are_ignored() -> None:
    task = HomeMaintenanceTask.from_dict(
        {
            "id": "home_maintenance_future",
            "title": "Future proof",
            "interval_value": 1,
            "interval_type": "years",
            "last_performed": "2026-08-01T00:00:00+02:00",
            "unknown_future_field": "safe-to-ignore",
        }
    )
    assert task.id == "home_maintenance_future"
