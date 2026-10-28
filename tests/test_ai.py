"""Tests for validating AI suggestions."""

import pytest
from homeassistant.exceptions import HomeAssistantError

from custom_components.home_maintenance.ai import (
    TASK_STRUCTURE,
    sanitize_steps,
    sanitize_task,
    steps_instructions,
    task_instructions,
)


def test_good_answer_is_kept() -> None:
    proposal = sanitize_task(
        {
            "title": "Pulizia filtro lavastoviglie",
            "interval_value": 1,
            "interval_type": "months",
            "priority": "normal",
            "duration_minutes": 10,
            "icon": "mdi:dishwasher",
            "description": "Sciacqua il filtro sotto l'acqua calda.",
            "checklist": ["Estrai il filtro", "Sciacqua", "Rimonta"],
            "active_months": [],
        }
    )
    assert proposal == {
        "title": "Pulizia filtro lavastoviglie",
        "interval_value": 1,
        "interval_type": "months",
        "priority": "normal",
        "duration_minutes": 10,
        "icon": "mdi:dishwasher",
        "description": "Sciacqua il filtro sotto l'acqua calda.",
        "checklist": ["Estrai il filtro", "Sciacqua", "Rimonta"],
        "active_months": [],
    }


def test_bad_values_are_clamped_or_defaulted() -> None:
    proposal = sanitize_task(
        {
            "title": "  " + "x" * 200,
            "interval_value": "-4",
            "interval_type": "fortnights",
            "priority": "urgent",
            "duration_minutes": 99999,
            "icon": "<img src=x>",
            "checklist": "Uno\nDue\n\nTre\nQuattro\nCinque\nSei\nSette",
            "active_months": [13, "6", 6.4, None, 0],
        }
    )
    assert 0 < len(proposal["title"]) <= 80
    assert proposal["interval_value"] == 1
    assert proposal["interval_type"] == "months"
    assert proposal["priority"] == "normal"
    assert proposal["duration_minutes"] == 1440
    assert proposal["icon"] == "mdi:calendar-check"
    assert proposal["checklist"] == ["Uno", "Due", "Tre", "Quattro", "Cinque", "Sei"]
    assert proposal["active_months"] == [1, 6, 12]
    assert proposal["description"] == ""


def test_paragraph_title_is_cut_to_its_first_sentence() -> None:
    title = (
        "Pulizia del filtro della lavastoviglie per una manutenzione ottimale "
        "ed evitare cattivi odori. Segui questi passi essenziali per completare"
    )
    proposal = sanitize_task({"title": title})
    assert proposal["title"].startswith("Pulizia del filtro della lavastoviglie")
    assert len(proposal["title"]) <= 80
    assert not proposal["title"].endswith(" ")
    assert sanitize_task({"title": "Pulizia bagno."})["title"] == "Pulizia bagno"


def test_month_strings_from_multi_select_are_accepted() -> None:
    assert sanitize_task({"title": "T", "active_months": ["6", "7", "8"]})[
        "active_months"
    ] == [6, 7, 8]


def test_real_google_answer_round_trips() -> None:
    # Answer returned by ai_task.google_ai_task for the integration's prompt.
    answer = {
        "active_months": [],
        "checklist": [
            "Estrarre il cestello inferiore della lavastoviglie",
            "Svitare e rimuovere il filtro posto sul fondo",
            "Sciacquare il filtro sotto acqua corrente calda",
            "Rimuovere eventuali residui di cibo con una spazzola morbida",
            "Reinserire il filtro e avvitarlo correttamente in sede",
        ],
        "description": "Una pulizia regolare del filtro previene cattivi odori.",
        "duration_minutes": 10,
        "icon": "mdi:dishwasher",
        "interval_type": "months",
        "interval_value": 1,
        "priority": "normal",
        "title": "Pulizia filtro lavastoviglie",
    }
    proposal = sanitize_task(answer)
    assert proposal["title"] == "Pulizia filtro lavastoviglie"
    assert len(proposal["checklist"]) == 5
    assert proposal["icon"] == "mdi:dishwasher"


def test_all_months_means_all_year() -> None:
    proposal = sanitize_task({"title": "T", "active_months": list(range(1, 13))})
    assert proposal["active_months"] == []


@pytest.mark.parametrize("answer", [None, "text", {"title": " "}])
def test_unusable_answers_are_rejected(answer: object) -> None:
    with pytest.raises(HomeAssistantError):
        sanitize_task(answer)


def test_steps() -> None:
    assert sanitize_steps({"checklist": [" A ", "", "B"]}) == ["A", "B"]
    with pytest.raises(HomeAssistantError):
        sanitize_steps({"checklist": []})
    with pytest.raises(HomeAssistantError):
        sanitize_steps("nope")


def test_prompts_carry_request_and_language() -> None:
    prompt = task_instructions("pulire il filtro", "Italian")
    assert "pulire il filtro" in prompt
    assert "Italian" in prompt
    prompt = steps_instructions("Bagno", "Anche la doccia", "Italian")
    assert "Bagno" in prompt
    assert "Anche la doccia" in prompt


def test_structure_uses_valid_selectors() -> None:
    for spec in TASK_STRUCTURE.values():
        assert len(spec["selector"]) == 1
        kind, config = next(iter(spec["selector"].items()))
        assert kind in {"text", "number", "select"}
        # ai_task rejects multiple number selectors (HTTP 400 on a real install).
        assert not (kind == "number" and (config or {}).get("multiple"))
