# services/agent_service/tools/router.py

import asyncio

from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("ToolRegistry"), {})

TOOLS = {}


def register_tool(name: str, description: str, func):

    if name in TOOLS:
        logger.debug(f"TOOL {name} already registered")
        return

    TOOLS[name] = {
        "description": description,
        "func": func
    }

    logger.debug(f"REGISTER TOOL {name}")


async def run_tool(name: str, args: dict):

    if name not in TOOLS:
        raise ValueError(f"Tool '{name}' is not registered")

    func = TOOLS[name]["func"]

    if asyncio.iscoroutinefunction(func):
        return await func(**args)
    else:
        return func(**args)


def list_tools():
    return TOOLS


def generate_tool_prompt():
    text = "Доступные инструменты:\n\n"

    for name, meta in TOOLS.items():
        text += f"{name} — {meta['description']}\n"

    return text
