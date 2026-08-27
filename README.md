# 🏠 Home Maintenance for Home Assistant

Track recurring home-maintenance tasks directly in Home Assistant, with due dates, history, reminders, NFC completion, automation hooks and a dedicated responsive panel.

Maintained by **Giuseppe Barchetta** ([@giuseppe99barchetta](https://github.com/giuseppe99barchetta)).

## ✨ Features

- 📅 Recurring schedules in **days, weeks, months or years**
- ✅ Completion history for every task
- ⏰ Due, overdue and next-7-days timeline
- 💤 **Snooze** a task without pretending it was completed
- ↷ **Skip** only the current occurrence while preserving history
- 🔔 Configurable Home Assistant persistent notifications before a task is due
- 🏷️ Search, status filters and grouping by Home Assistant labels
- 📱 Responsive panel designed for desktop and mobile
- 📊 Aggregate completed, skipped and snoozed statistics
- 📝 Optional task notes and reference URLs
- 📲 NFC tag completion
- ⚡ Optional automatic completion when a Home Assistant entity reaches a configured state
- 🧰 Home Assistant services and events for automations
- ↥/↧ JSON import and export for backup or migration
- 🚀 Built-in presets for common maintenance jobs
- 🔄 Existing task data is migrated transparently when upgrading

## 🖼️ Screenshots

The existing screenshots in this repository may show an older panel version. They will be refreshed after the v2 interface has been exercised in a live Home Assistant installation.

## 🛠️ Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=giuseppe99barchetta&repository=home_maintenance&category=Integration)

### HACS

1. Open HACS.
2. Add `https://github.com/giuseppe99barchetta/home_maintenance` as a custom **Integration** repository if needed.
3. Install **Home Maintenance**.
4. Restart Home Assistant.
5. Go to **Settings → Devices & services → Add integration** and add **Home Maintenance**.
6. Open **Home Maintenance** from the Home Assistant sidebar.

HACS installs directly from the repository; a custom release ZIP is not required.

### Manual installation

Download the repository source and copy:

```text
custom_components/home_maintenance
```

into your Home Assistant `custom_components` directory, then restart Home Assistant and add the integration from **Settings → Devices & services**.

## 🧭 Using the panel

The panel provides two main views:

- **Timeline** groups tasks into overdue, due today, due soon and later.
- **By label** groups tasks using Home Assistant labels.

Each task can be completed, snoozed for three days, skipped, edited or deleted. The history dialog shows recorded completions and skipped occurrences.

When creating or editing a task you can configure:

- title and recurrence interval;
- last-performed date;
- notes / description and a reference URL;
- icon and Home Assistant labels;
- NFC tag;
- notification lead time;
- an optional entity and target state for automatic completion.

Quick presets are available for common jobs such as HVAC filters, smoke-detector checks, water filters and boiler servicing.

## 🔔 Notifications

Enable notifications on an individual task and choose how many days before the due date to start notifying.

Home Maintenance checks notification-enabled tasks every day and creates a Home Assistant persistent notification once per day while a task is inside its configured notification window. It also fires a `home_maintenance_task_due` event that can be used to build your own mobile, Telegram or voice notification automation.

## ⚡ Smart completion

A task can optionally reference a Home Assistant entity and a target state. When that entity changes to the configured state, the task is completed automatically and the completion is recorded in history.

Example use cases include completing a maintenance task when a counter is reset, a helper is toggled, or another integration reports a known completion state.

## 📲 NFC tags

Associate a Home Assistant `tag.*` entity with a task. Scanning the underlying tag completes the task and records the completion source as NFC.

## 🔁 Home Assistant services

The integration exposes the following services:

| Service | Purpose |
| --- | --- |
| `home_maintenance.create_task` | Create a recurring task |
| `home_maintenance.complete_task` | Complete a task now |
| `home_maintenance.reset_last_performed` | Complete a task using an optional historical date |
| `home_maintenance.snooze_task` | Postpone a task without changing completion history |
| `home_maintenance.skip_task` | Skip only the current occurrence |
| `home_maintenance.delete_task` | Permanently delete a task |

Example:

```yaml
service: home_maintenance.snooze_task
data:
  entity_id: binary_sensor.clean_gutters
  days: 7
```

## 📣 Events

Home Maintenance fires these events:

| Event | When |
| --- | --- |
| `home_maintenance_task_completed` | A task is completed manually, through NFC or by an entity state |
| `home_maintenance_task_skipped` | The current occurrence is skipped |
| `home_maintenance_task_due` | A notification-enabled task enters or remains inside its due window |

The completion event includes the task ID, title and completion source where available.

## 🧩 Entity attributes

Each task is represented by a binary sensor and exposes useful attributes including:

- `last_performed`
- `next_due`
- `days_remaining`
- `overdue_days`
- `interval_value` / `interval_type`
- `snoozed_until`
- `history_count`
- `skipped_count`
- notification settings
- description / URL
- smart-completion entity and target state
- NFC tag when configured

The sensor turns on when the task is due or overdue.

## 💾 Import / export

The panel can export all task data to JSON and later import it again. This includes the extended task settings and history stored by Home Maintenance.

Existing pre-v2 tasks remain compatible: missing v2 fields are populated with safe defaults when storage is loaded.

## 🧪 Development and validation

The repository runs:

- Ruff linting and formatting checks;
- backend pytest coverage for scheduling and storage compatibility;
- frontend JavaScript syntax checks;
- Home Assistant/Hassfest validation;
- HACS validation where applicable.

Scheduling tests specifically cover month-end behavior, leap years, yearly intervals, snooze/skip overrides and DST-safe calendar-day comparisons.

## 💬 Support

Open an issue in the [GitHub issue tracker](https://github.com/giuseppe99barchetta/home_maintenance/issues) or use the Home Assistant community thread:

[Home Assistant Community Thread](https://community.home-assistant.io/t/new-integration-home-maintenance-track-recurring-tasks-in-home-assistant/897324)

## 📄 License

MIT License – free to use, share and improve. Existing copyright and attribution notices remain preserved in the license file.
