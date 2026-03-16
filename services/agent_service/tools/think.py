import asyncio

from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("ThinkTool"), {})


async def think_tool(thought_process: str = ""):
    """
    Инструмент внутреннего размышления агента.
    """

    logger.debug(f"[AGENT THINK] {thought_process}")

    await asyncio.sleep(0.05)

    return {
        "result": thought_process
    }


# регистрация инструмента
'''
register_tool(
    name="think",
    description="Internal reasoning tool",
    func=think_tool
)
'''
