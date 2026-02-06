"""Domain models for PC parts and builds."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Part:
    """A single PC component with display name, price, and optional link."""

    category: str
    name: str
    price: str
    link: Optional[str] = None

    @property
    def display_name(self) -> str:
        return f"{self.category}: {self.name}"

    def price_float(self) -> float:
        return float(self.price.replace(",", "").strip())


@dataclass
class Build:
    """A full PC build: list of parts and optional tax rate."""

    parts: list[Part]
    tax_rate: float = 0.0

    def subtotal(self) -> float:
        return sum(p.price_float() for p in self.parts)

    def total(self) -> float:
        return round(self.subtotal() * (1 + self.tax_rate), 2)

    def part_count(self) -> int:
        return len(self.parts)
