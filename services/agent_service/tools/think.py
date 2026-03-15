# services/agent_service/tools/think.py

import asyncio

from services.agent_service.tools.tool_registry import register_tool
from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("ThinkTool"), {})


async def think_tool(thought: str = "", question: str = "") -> dict:
    """
    Асинхронный инструмент внутреннего размышления.
    Принимает 'thought' или 'question', возвращает результат анализа.
    """
    text = thought or question or ""
    logger.debug(f"[AGENT THINK] {text}")

    # Симуляция внутреннего размышления
    await asyncio.sleep(0.05)

    return {"result": text}


# регистрация инструмента
register_tool("think", "Internal reasoning tool", think_tool)
