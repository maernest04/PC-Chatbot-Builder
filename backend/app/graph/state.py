"""Graph state for the PC builder agent."""

from typing import Annotated, Literal, TypedDict

from langgraph.graph.message import add_messages


class BuilderState(TypedDict, total=False):
    """State for the conversation and build flow."""

    messages: Annotated[list, add_messages]
    budget: float
    preferences: str
    region: str
    current_build: list[dict]  # part snapshots
    build_total: dict  # subtotal, tax_rate, total
