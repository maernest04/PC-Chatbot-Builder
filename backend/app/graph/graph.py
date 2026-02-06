"""Compile the PC builder agent graph with optional persistence."""

import os
import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

from app.graph.nodes import llm_node, should_continue, tool_node
from app.graph.state import BuilderState


def compile_graph(use_checkpointer: bool = True):
    """Build and compile the agent graph. Optionally use SQLite checkpointer for persistence."""
    builder = StateGraph(BuilderState)

    builder.add_node("llm", llm_node)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "llm")
    builder.add_conditional_edges("llm", should_continue, ["tools", END])
    builder.add_edge("tools", "llm")

    if use_checkpointer:
        conn = sqlite3.connect(
            os.environ.get("CHECKPOINT_DB", "checkpoints.sqlite"),
            check_same_thread=False,
        )
        checkpointer = SqliteSaver(conn)
        return builder.compile(checkpointer=checkpointer)
    return builder.compile()
