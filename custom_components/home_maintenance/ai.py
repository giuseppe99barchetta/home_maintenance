"""
AI helpers for Home Maintenance.

Home Maintenance never talks to a model directly: it asks the AI Task entity
the user already configured in Home Assistant (OpenAI, Google, Ollama, ...)
through the ``ai_task.generate_data`` action and expects structured data back.
Every answer is validated and normalized here, and is only ever shown to the
user as a proposal: nothing is created or changed without confirmation.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import HomeAssistantError

from .schedule import INTERVAL_TYPES, PRIORITIES
from .store import normalize_checklist

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

AI_DOMAIN = "ai_task"
AI_SERVICE = "generate_data"
OPTION_AI_ENTITY = "ai_task_entity"
MAX_DESCRIPTION = 500
MAX_TITLE = 80
DEFAULT_ICON = "mdi:calendar-check"
_ICON_RE = re.compile(r"^mdi:[a-z0-9]+(-[a-z0-9]+)*$")

_LANGUAGES = {"it": "Italian", "de": "German", "en": "English"}

TASK_STRUCTURE: dict[str, Any] = {
    "title": {
        "description": "Short task name, max 60 characters",
        "required": True,
        "selector": {"text": {}},
    },
    "interval_value": {
        "description": "How many units between two occurrences",
        "required": True,
        "selector": {"number": {"min": 1, "max": 3650}},
    },
    "interval_type": {
        "description": "Unit of the interval",
        "required": True,
        "selector": {"select": {"options": list(INTERVAL_TYPES)}},
    },
    "priority": {
        "description": "high for safety, health, pets or costly damage; low for "
        "purely cosmetic jobs; normal otherwise",
        "required": True,
        "selector": {"select": {"options": list(PRIORITIES)}},
    },
    "duration_minutes": {
        "description": "Realistic time needed, in minutes",
        "selector": {"number": {"min": 1, "max": 1440}},
    },
    "icon": {
        "description": "Material Design Icon in the form mdi:name",
        "selector": {"text": {}},
    },
    "description": {
        "description": "One or two sentences of practical notes",
        "selector": {"text": {}},
    },
    "checklist": {
        "description": "2 to 6 short, concrete steps, without numbering",
        "selector": {"text": {"multiple": True}},
    },
    # A multiple number selector is rejected by ai_task: use a multi-select.
    "active_months": {
        "description": "Months when the task applies; empty for all year",
        "selector": {
            "select": {"multiple": True, "options": [str(m) for m in range(1, 13)]}
        },
    },
}

STEPS_STRUCTURE: dict[str, Any] = {
    "checklist": {
        "description": "2 to 6 short, concrete steps, without numbering",
        "required": True,
        "selector": {"text": {"multiple": True}},
    },
}


class AIUnavailableError(HomeAssistantError):
    """No AI Task entity is available."""


def available_entities(hass: HomeAssistant) -> list[dict[str, str]]:
    """Return the AI Task entities that can generate data."""
    if not hass.services.has_service(AI_DOMAIN, AI_SERVICE):
        return []
    return [
        {"entity_id": state.entity_id, "name": state.name}
        for state in hass.states.async_all(AI_DOMAIN)
        if state.state != "unavailable"
    ]


def configured_entity(hass: HomeAssistant, options: dict[str, Any]) -> str | None:
    """Return the AI Task entity to use, or None to use Home Assistant's default."""
    wanted = options.get(OPTION_AI_ENTITY) or None
    known = {item["entity_id"] for item in available_entities(hass)}
    return wanted if wanted in known else None


def _language(hass: HomeAssistant) -> str:
    return _LANGUAGES.get((hass.config.language or "en").split("-")[0], "English")


def task_instructions(description: str, language: str) -> str:
    """Prompt for turning a free-text request into one recurring task."""
    return (
        "You help people keep their home maintained. Turn the request below into "
        "ONE recurring home-maintenance task. Write every text field in "
        f"{language}. Use a realistic frequency for a typical household, a "
        "realistic duration, and practical steps someone can follow without "
        "tools they would not normally own. Only set active_months for jobs "
        "that truly depend on the season.\n\n"
        f"Request: {description}"
    )


def steps_instructions(title: str, description: str | None, language: str) -> str:
    """Prompt for a checklist of an existing task."""
    notes = f"\nNotes: {description}" if description else ""
    return (
        "You help people keep their home maintained. Split the task below into "
        f"2 to 6 short, concrete steps, in {language}, in the order they are "
        "done. Each step is one action, no numbering, no explanations.\n\n"
        f"Task: {title}{notes}"
    )


def _number(value: Any, low: int, high: int) -> int | None:
    try:
        number = round(float(value))
    except (TypeError, ValueError):
        return None
    return max(low, min(high, number))


def _short_title(value: Any) -> str:
    """
    Return a usable task name.

    Some models occasionally pour the whole answer into the title; keep the
    first sentence and cut long names at a word boundary.
    """
    text = " ".join(str(value or "").split())
    for stop in (". ", "! ", "? ", ": "):
        if stop in text:
            text = text.split(stop, 1)[0]
    if len(text) > MAX_TITLE:
        text = text[:MAX_TITLE].rsplit(" ", 1)[0].rstrip(",;-")
    return text.rstrip(".").strip()


def sanitize_task(data: Any) -> dict[str, Any]:
    """Validate an AI answer and return a safe task proposal."""
    if not isinstance(data, dict):
        msg = "The AI answer was not structured data."
        raise HomeAssistantError(msg)
    title = _short_title(data.get("title"))
    if not title:
        msg = "The AI answer had no task name."
        raise HomeAssistantError(msg)
    interval_type = str(data.get("interval_type") or "").strip().lower()
    if interval_type not in INTERVAL_TYPES:
        interval_type = "months"
    priority = str(data.get("priority") or "").strip().lower()
    icon = str(data.get("icon") or "").strip().lower()
    months = data.get("active_months") or []
    if not isinstance(months, (list, tuple)):
        months = [months]
    clean_months = sorted({m for m in (_number(x, 1, 12) for x in months) if m})
    return {
        "title": title,
        "interval_value": _number(data.get("interval_value"), 1, 3650) or 1,
        "interval_type": interval_type,
        "priority": priority if priority in PRIORITIES else "normal",
        "duration_minutes": _number(data.get("duration_minutes"), 1, 1440),
        "icon": icon if _ICON_RE.match(icon) else DEFAULT_ICON,
        "description": str(data.get("description") or "").strip()[:MAX_DESCRIPTION],
        "checklist": normalize_checklist(data.get("checklist"))[:6],
        "active_months": [] if len(clean_months) == 12 else clean_months,  # noqa: PLR2004
    }


def sanitize_steps(data: Any) -> list[str]:
    """Validate an AI answer with checklist steps."""
    steps = normalize_checklist(
        data.get("checklist") if isinstance(data, dict) else None
    )
    if not steps:
        msg = "The AI answer had no steps."
        raise HomeAssistantError(msg)
    return steps[:6]


async def _generate(
    hass: HomeAssistant,
    entity_id: str | None,
    task_name: str,
    instructions: str,
    structure: dict[str, Any],
) -> Any:
    """Call ai_task.generate_data and return its data."""
    if not available_entities(hass):
        msg = "No AI Task entity is set up in Home Assistant."
        raise AIUnavailableError(msg)
    payload: dict[str, Any] = {
        "task_name": task_name,
        "instructions": instructions,
        "structure": structure,
    }
    if entity_id:
        payload["entity_id"] = entity_id
    response = await hass.services.async_call(
        AI_DOMAIN,
        AI_SERVICE,
        payload,
        blocking=True,
        return_response=True,
    )
    return (response or {}).get("data")


async def async_suggest_task(
    hass: HomeAssistant, description: str, entity_id: str | None
) -> dict[str, Any]:
    """Ask the AI for a task proposal from a free-text description."""
    text = description.strip()[:MAX_DESCRIPTION]
    if not text:
        msg = "Describe the task first."
        raise HomeAssistantError(msg)
    data = await _generate(
        hass,
        entity_id,
        "Home Maintenance task suggestion",
        task_instructions(text, _language(hass)),
        TASK_STRUCTURE,
    )
    return sanitize_task(data)


async def async_suggest_steps(
    hass: HomeAssistant, title: str, description: str | None, entity_id: str | None
) -> list[str]:
    """Ask the AI for checklist steps for a task."""
    name = title.strip()[:MAX_TITLE]
    if not name:
        msg = "Give the task a name first."
        raise HomeAssistantError(msg)
    data = await _generate(
        hass,
        entity_id,
        "Home Maintenance checklist suggestion",
        steps_instructions(
            name, (description or "").strip()[:MAX_DESCRIPTION], _language(hass)
        ),
        STEPS_STRUCTURE,
    )
    return sanitize_steps(data)
