# services/agent_service/tools/think.py

import asyncio
from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("ThinkTool"), {})


async def think_tool(thought_process: str = ""):
    """
    ⚠️ DEPRECATED TOOL

    Этот инструмент больше не должен использоваться LLM.
    THINK теперь реализован внутри AgentLoop.

    Оставлен только для совместимости.
    """

    logger.warning("think_tool SHOULD NOT BE USED")

    await asyncio.sleep(0.01)

    return {
        "result": "internal reasoning disabled"
    }


# ❌ НЕ РЕГИСТРИРУЕМ
# register_tool(...)