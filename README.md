# 🏠 Home Maintenance Tracker for Home Assistant

Keep your home in top shape by tracking recurring maintenance tasks right inside Home Assistant!

This custom integration helps you remember important chores like changing air filters, cleaning gutters, or testing smoke alarms — and shows you when they're due.

Maintained by **Giuseppe Barchetta** ([@giuseppe99barchetta](https://github.com/giuseppe99barchetta)).

---

## ✨ What It Does

- 📋 Lets you create recurring tasks (e.g., “Change HVAC filter every 90 days”)
- 🔔 Creates entities in Home Assistant to be able to create automations and display on dashboards
- ✅ Lets you mark tasks as completed so it can track the next due date
- 📊 Shows tasks in a clean, responsive interface built into Home Assistant

---

## ⚠️ Important Note
This integration was created to fill a simple but important gap in Home Assistant: the ability to create recurring tasks without relying on multiple helpers and automations. It is intentionally focused on recurring home-maintenance task tracking.

Home Assistant already provides powerful features for dashboards, automations, and alerts, and this integration is meant to complement those, not replace them.

Because it's a custom component with limited scope and resources, not all feature requests will be added or considered — especially if the functionality already exists natively in Home Assistant or falls outside the intended purpose of the integration.

Thank you for understanding and helping keep this integration focused and maintainable.

---

## 🖼️ Screenshots

- ![Task Panel](screenshots/task-panel.PNG)
- ![Integration Page](screenshots/integration-page.PNG)
- ![Entity Attributes](screenshots/entity-attributes.PNG)

---

## 🛠️ Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=giuseppe99barchetta&repository=home_maintenance&category=Integration)

<details>
<summary>Click to show installation instructions</summary>
<ol>
<li>Install files:</li>
<ul>
<li><u>Using HACS:</u><br>
In HACS, add <code>https://github.com/giuseppe99barchetta/home_maintenance</code> as a custom integration repository if it is not already available, then download Home Maintenance.</li>
<li><u>Manually:</u><br>
Download the <a href="https://github.com/giuseppe99barchetta/home_maintenance/releases">latest release</a> as a zip file and extract it into the <code>custom_components</code> folder in your Home Assistant installation.</li>
</ul>
<li>Restart Home Assistant to load the integration.</li>
<li>Go to Settings -> Devices & services and click 'ADD INTEGRATION'. Look for Home Maintenance and add it.</li>
<li>The Home Maintenance integration is ready for use. You can find its panel in the Home Assistant sidebar.</li>
</ol>
</details>

---

## 🛠️ How to Use

- Open **Home Maintenance** from the Home Assistant sidebar.
- To add a new task enter:
  - A title (e.g., “Clean Dryer Vent”)
  - How often it needs to be done
  - Select the interval period (defaults to days)
  - The last time you did it (optional; if omitted, today is used)
  - Select an NFC tag (optional; scanning it marks the task complete)
  - Select an icon (optional)
  - Select labels (optional)
  - Click **Add Task**
- Use search and status filters to find due, overdue, or later tasks.
- Click **Complete** to reset the Last Performed date to today.

---

## 🔄 Example Tasks

| Task                 | Interval | Last Done     |
|----------------------|----------|---------------|
| Change HVAC Filter   | 90 days  | Jan 15, 2025  |
| Test Smoke Alarms    | 6 months | Dec 1, 2024   |
| Clean Gutters        | 8 weeks  | Oct 1, 2024   |

---

## 🔁 Available Services

### `home_maintenance.reset_last_performed`

Marks a specific task as completed and updates its `last_performed` and `next_due`.

Optionally specify a date for `last_performed`.

#### Example service call:

```yaml
service: home_maintenance.reset_last_performed
data:
  entity_id: binary_sensor.clean_gutters
  performed_date: "2025-06-19"
```

---

## 💬 Need Help?

Open an issue in the [GitHub issue tracker](https://github.com/giuseppe99barchetta/home_maintenance/issues) or ask in the Home Assistant community.

[Home Assistant Community Thread](https://community.home-assistant.io/t/new-integration-home-maintenance-track-recurring-tasks-in-home-assistant/897324)

---

## 📄 License

MIT License – free to use, share, and improve. Existing copyright and attribution notices remain preserved in the license file.
