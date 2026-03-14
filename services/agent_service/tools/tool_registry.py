# services/agent_service/tools/tool_registry.py
import asyncio
from services.utils.logger import get_logger, TraceAdapter

base_logger = get_logger("ToolRegistry")
logger = TraceAdapter(base_logger, {})

TOOLS = {}


def register_tool(name, description, func):
    if name in TOOLS:
        logger.debug(f"TOOL {name} already registered")
        return
    logger.debug(f"REGISTER TOOL {name}")
    TOOLS[name] = {
        "description": description,
        "func": func
    }


def get_tool(name):
    return TOOLS.get(name)


def list_tools():
    return TOOLS


def generate_tool_prompt():
    prompt = "Available tools:\n\n"
    for name, tool in TOOLS.items():
        desc = tool["description"]
        prompt += f"{name} - {desc}\n"
    return prompt


async def run_tool(name, args=None):
    """
    Запускает инструмент по имени.
    Поддерживает async и sync функции.
    """
    tool = TOOLS.get(name)
    if not tool:
        raise ValueError(f"Tool '{name}' not found")

    func = tool["func"]
    if args is None:
        args = {}

    if asyncio.iscoroutinefunction(func):
        return await func(**args)
    else:
        return func(**args)
