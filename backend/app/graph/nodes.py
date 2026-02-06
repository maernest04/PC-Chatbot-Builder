"""Graph nodes: LLM with tools and tool execution."""

from typing import Literal

from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session

from app.graph.state import BuilderState
from app.tools.build import get_build_total
from app.tools.parts import search_parts as search_parts_impl

SYSTEM_PROMPT = """You are a helpful PC building assistant. Have a natural conversation—don't run through a fixed list of questions. React to what the user says and only ask for details when you need them (e.g. budget, what they'll use the PC for, or state/region for tax). If they volunteer several things at once (e.g. "I have $1500 for gaming in California"), use that and suggest a build when you have enough.

You have tools:
- search_parts(category, max_price?): look up parts from our catalog. Categories: CPU, CPU Cooler, Motherboard, Memory, Storage, GPU, Case, Power Supply.
- get_build_total(part_ids, region): get subtotal, tax, and total for part IDs and a US state/region.

When suggesting a build: use search_parts for each category with max prices that fit the budget (reserve ~$120 for Windows if they want an OS), then get_build_total with their state. Present parts and total clearly. If they want changes (different GPU, more storage, etc.), call the tools again. Be concise and friendly."""


def create_llm(model: str = "gpt-4o-mini"):
    return ChatOpenAI(model=model, temperature=0)


def make_tools(db: Session):
    """Build tools that close over the db session for this request."""

    def search_parts_tool(category: str, max_price: float | None = None, limit: int = 10) -> str:
        """Search for PC parts by category. max_price is optional (USD). Returns a list of parts with id, name, price_usd, link."""
        import json
        parts = search_parts_impl(db, category=category, max_price=max_price, limit=limit)
        return json.dumps([{"id": p["id"], "name": p["name"], "price_usd": p["price_usd"], "link": p.get("link")} for p in parts])

    def get_build_total_tool(part_ids: list[str], region: str) -> str:
        """Compute subtotal, tax rate, and total for a list of part IDs (from search_parts) and a US state or region (e.g. CA or California)."""
        import json
        result = get_build_total(db, part_ids=part_ids, region=region)
        return json.dumps({"subtotal": result["subtotal"], "tax_rate": result["tax_rate"], "total": result["total"], "parts": result["parts"]})

    from langchain_core.tools import tool

    @tool
    def search_parts(category: str, max_price: float | None = None, limit: int = 10) -> str:
        """Search for PC parts by category. category must be one of: CPU, CPU Cooler, Motherboard, Memory, Storage, GPU, Case, Power Supply. max_price is optional (USD)."""
        return search_parts_tool(category, max_price, limit)

    @tool
    def get_build_total(part_ids: list[str], region: str) -> str:
        """Compute subtotal, tax rate, and total for a list of part IDs and a US state/region (e.g. CA or California)."""
        return get_build_total_tool(part_ids, region)

    return [search_parts, get_build_total]


def _get_db(config: RunnableConfig) -> Session:
    db = (config or {}).get("configurable", {}).get("db")
    if db is None:
        raise ValueError("config['configurable']['db'] is required")
    return db


def llm_node(state: BuilderState, config: RunnableConfig):
    """Invoke LLM with tools; append response to messages."""
    db = _get_db(config)
    tools = make_tools(db)
    llm = create_llm().bind_tools(tools)

    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)

    response = llm.invoke(messages)
    return {"messages": [response]}


def tool_node(state: BuilderState, config: RunnableConfig):
    """Execute tool calls from the last message and return ToolMessages. Persist build when get_build_total is used."""
    import json
    db = _get_db(config)
    configurable = (config or {}).get("configurable") or {}
    thread_id = configurable.get("thread_id")

    tools = make_tools(db)
    tools_by_name = {t.name: t for t in tools}

    messages = state["messages"]
    last = messages[-1]
    if not hasattr(last, "tool_calls") or not last.tool_calls:
        return {"messages": []}

    result = []
    for tc in last.tool_calls:
        name = tc["name"]
        args = tc.get("args") or {}
        tool = tools_by_name.get(name)
        if tool:
            out = tool.invoke(args)
            result.append(ToolMessage(content=str(out), tool_call_id=tc["id"]))
            if name == "get_build_total" and thread_id:
                try:
                    data = json.loads(out)
                    from app.db.sessions import create_build
                    create_build(
                        db,
                        session_id=thread_id,
                        parts=data.get("parts") or [],
                        subtotal=float(data.get("subtotal", 0)),
                        tax_rate=float(data.get("tax_rate", 0)),
                        total=float(data.get("total", 0)),
                    )
                except Exception:
                    pass
        else:
            result.append(ToolMessage(content=f"Unknown tool: {name}", tool_call_id=tc["id"]))
    return {"messages": result}


def should_continue(state: BuilderState) -> Literal["tools", "end"]:
    """Route to tools if last message has tool_calls, else end."""
    messages = state["messages"]
    if not messages:
        return "end"
    last = messages[-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "end"
