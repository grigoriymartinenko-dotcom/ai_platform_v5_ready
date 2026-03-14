# services/agent_service/tools/router.py
import sys
import asyncio
from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("ToolRegistry"), {})

TOOLS = {}


def register_tool(name: str, description: str, func):
    if name in TOOLS:
        logger.debug(f"TOOL {name} already registered")
        return
    TOOLS[name] = {"description": description, "func": func}
    logger.debug(f"REGISTER TOOL {name}")


async def run_tool(name: str, args: dict):
    if name not in TOOLS:
        raise ValueError(f"Tool '{name}' is not registered")
    func = TOOLS[name]["func"]
    if asyncio.iscoroutinefunction(func):
        return await func(**args)
    else:
        return func(**args)


# ----------------- Инструменты -----------------
def think_tool(thought: str = ""):
    return {"result": f"[AGENT THINK] {thought}"}


def plan_tool(task: str = ""):
    return {"result": f"[AGENT PLAN] {task}"}


def web_search_tool(query: str = ""):
    return {"result": f"[WEB SEARCH] {query}"}


def read_page_tool(url: str = ""):
    return {"result": f"[READ PAGE] {url}"}


# ----------------- Регистрируем один раз -----------------
if not hasattr(sys.modules[__name__], "_TOOLS_REGISTERED"):
    register_tool("think", "Внутренние размышления агента", think_tool)
    register_tool("plan", "Планирование действий агента", plan_tool)
    register_tool("web_search", "Поиск в интернете", web_search_tool)
    register_tool("read_page", "Чтение веб-страницы", read_page_tool)
    from .calculator import calculator
    from .weather import weather

    register_tool("calculator", "Calculate math expression", calculator)
    register_tool("weather", "Get weather for city", weather)
    setattr(sys.modules[__name__], "_TOOLS_REGISTERED", True)
