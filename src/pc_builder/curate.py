"""Part curation: use LLM to suggest parts and price lookup to build a full Build."""

import logging
import re
from typing import Optional

from pc_builder.llm import ChatSession
from pc_builder.models import Build, Part
from pc_builder.price_lookup import PART_CATEGORIES, PriceLookup

logger = logging.getLogger(__name__)

# Windows 11 Home as a fixed part
OS_PART = Part(
    category="Operating System",
    name="Windows 11 Home",
    price="119.99",
    link="https://www.amazon.com/s?k=Windows+11+Home",
)


def parse_tax_rate(raw: str) -> float:
    """Parse LLM response to a float tax rate (e.g. 0.0725)."""
    raw = (raw or "").strip()
    # Remove common suffixes/prefixes
    raw = re.sub(r"%|percent|tax\s*rate\s*[:=]?", "", raw, flags=re.IGNORECASE)
    raw = raw.strip()
    try:
        return float(raw)
    except ValueError:
        return 0.0


def parse_part_list(response: str) -> list[str]:
    """Parse comma-separated part names from LLM response. Expects 8 parts."""
    parts = [p.strip() for p in response.split(",") if p.strip()]
    return parts[:8] if len(parts) >= 8 else parts


def curate_parts(
    chat: ChatSession,
    price_lookup: PriceLookup,
    preferences: str,
    budget: float,
    tax_rate: float,
    max_attempts: int = 5,
) -> Optional[Build]:
    """
    Get part suggestions from the LLM, resolve prices, and return a Build within budget.
    Budget is total including tax; we reserve ~120 for OS and aim for subtotal + tax <= budget.
    """
    target_subtotal = budget - 120.0  # reserve for OS
    if target_subtotal <= 0:
        return None

    for attempt in range(max_attempts):
        response = chat.get_part_list_response(preferences, target_subtotal)
        names = parse_part_list(response)
        if len(names) < 8:
            chat.say(
                "You must return exactly 8 comma-separated part names (CPU, CPU Cooler, Motherboard, "
                "Memory, Storage, GPU, Case, Power Supply). Try again with only that list."
            )
            continue

        parts: list[Part] = []
        for i, name in enumerate(names):
            cat = PART_CATEGORIES[i] if i < len(PART_CATEGORIES) else "Other"
            part = price_lookup.lookup(cat, name)
            if part is None:
                chat.say(f"Part '{name}' could not be found. Suggest a different part for {cat}.")
                break
            parts.append(part)

        if len(parts) < 8:
            continue

        parts.append(OS_PART)
        build = Build(parts=parts, tax_rate=tax_rate)
        total = build.total()

        if total > budget:
            chat.say(
                f"The total ${total:.2f} exceeded the budget ${budget:.2f}. "
                "Suggest a revised list with cheaper parts where needed."
            )
            continue

        return build

    return None
