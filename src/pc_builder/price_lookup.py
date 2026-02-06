"""Price lookup for parts. Implementations can use APIs or static data (no scraping)."""

import logging
import re
from abc import ABC, abstractmethod
from typing import Optional

from pc_builder.models import Part

logger = logging.getLogger(__name__)

# Standard categories for an 8-part + OS build
PART_CATEGORIES = [
    "CPU",
    "CPU Cooler",
    "Motherboard",
    "Memory",
    "Storage",
    "GPU",
    "Case",
    "Power Supply",
]

# Fallback placeholder when a part cannot be resolved
PLACEHOLDER_LINK = "https://www.amazon.com/s?k="


class PriceLookup(ABC):
    """Abstract interface for resolving part names to Part (name, price, link)."""

    @abstractmethod
    def lookup(self, category: str, product_name: str) -> Optional[Part]:
        """Return Part if found, else None."""
        ...


class MockPriceLookup(PriceLookup):
    """
    Mock lookup: returns Part with placeholder price and search link.
    Use for development or pair with a real price API (e.g. Rainforest API, manual data).
    """

    # Example prices (USD) per category for demo builds
    DEFAULT_PRICES: dict[str, str] = {
        "CPU": "300.00",
        "CPU Cooler": "120.00",
        "Motherboard": "200.00",
        "Memory": "120.00",
        "Storage": "110.00",
        "GPU": "550.00",
        "Case": "100.00",
        "Power Supply": "120.00",
        "Operating System": "119.99",
    }

    def lookup(self, category: str, product_name: str) -> Optional[Part]:
        clean_name = (product_name or "").strip()
        if not clean_name:
            return None
        price = self.DEFAULT_PRICES.get(category, "0.00")
        search = re.sub(r"\s+", "+", clean_name)
        link = f"{PLACEHOLDER_LINK}{search}"
        return Part(category=category, name=clean_name, price=price, link=link)
