# services/agent_service/tools/tool_registry.py
import asyncio

from services.utils.logger import get_logger, TraceAdapter

base_logger = get_logger("ToolRegistry")
logger = TraceAdapter(base_logger, {})

TOOLS = {}
REGISTERED = set()  # Для отслеживания уже зарегистрированных инструментов


def register_tool(name: str, description: str, func):
    """Регистрирует инструмент в глобальном реестре."""
    if name in REGISTERED:
        logger.info(f"Tool '{name}' is already registered, skipping...")
        return
    TOOLS[name] = {
        "description": description,
        "func": func
    }
    REGISTERED.add(name)
    logger.info(f"Registered tool '{name}'")


def get_tool(name: str):
    """Возвращает функцию инструмента по имени"""
    tool = TOOLS.get(name)
    if not tool:
        logger.error(f"Tool '{name}' not found")
        return None
    return tool["func"]


def list_tools():
    """Возвращает список всех зарегистрированных инструментов"""
    return list(TOOLS.keys())


async def run_tool(name: str, args: dict):
    """
    Выполняет инструмент по имени.
    Поддерживает асинхронные и синхронные функции.
    """
    func = get_tool(name)
    if not func:
        return f"Tool '{name}' not found"
    try:
        if asyncio.iscoroutinefunction(func):
            return await func(**args)
        else:
            return func(**args)
    except Exception as e:
        logger.error(f"Error running tool '{name}': {e}")
        return f"Error running tool '{name}': {e}"


def generate_tool_prompt() -> str:
    """
    Формирует текстовое описание всех инструментов для LLM.
    Возвращает строку со списком инструментов и их описанием.
    """
    prompt_lines = []
    for name, info in TOOLS.items():
        desc = info.get("description", "No description")
        prompt_lines.append(f"- {name}: {desc}")
    return "\n".join(prompt_lines)
