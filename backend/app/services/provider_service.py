"""Business logic for provider availability lookups."""

from typing import Any, Dict, List

from app.config.settings import get_settings
from app.repositories.provider_repository import provider_repository


def _free_slots_for_provider(provider_name: str) -> Dict[str, Any]:
    settings = get_settings()
    target = provider_repository.get_by_name(provider_name)

    if not target:
        return {
            "provider_name": provider_name,
            "found": False,
            "free_slots": [],
            "message": f"No provider named {provider_name}",
        }

    labels = target.get("slot_hour_labels") or settings.SLOT_HOUR_LABELS
    weekly = target.get("weekly_availability") or {}
    free_slots: List[Dict[str, str]] = []

    for weekday, slots in weekly.items():
        if not isinstance(slots, list):
            continue
        for i, flag in enumerate(slots):
            if flag == 0 and i < len(labels):
                free_slots.append({"weekday": weekday, "time": labels[i]})

    return {
        "provider_name": target.get("provider_name", provider_name),
        "found": True,
        "free_slots": free_slots,
        "message": f"{len(free_slots)} free slot(s) available",
    }


def get_availability(provider_name: str | None) -> Dict[str, Any]:
    if provider_name:
        return _free_slots_for_provider(provider_name)

    summaries = [
        _free_slots_for_provider(str(p.get("provider_name", "")))
        for p in provider_repository.list_all()
        if p.get("provider_name")
    ]
    return {"providers": summaries}
