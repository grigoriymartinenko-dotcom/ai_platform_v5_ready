# services/agent_service/tools/tool_registry.py

import asyncio
import inspect

from services.utils.logger import get_logger, TraceAdapter

base_logger = get_logger("ToolRegistry")
logger = TraceAdapter(base_logger, {})

TOOLS = {}
REGISTERED = set()


def register_tool(name: str, description: str, func):
    """
    Регистрирует инструмент в глобальном реестре.
    """

    if name in REGISTERED:
        logger.info(f"Tool '{name}' is already registered, skipping...")
        return

    signature = inspect.signature(func)

    params = []

    for p in signature.parameters.values():
        params.append(p.name)

    TOOLS[name] = {
        "description": description,
        "func": func,
        "params": params
    }

    REGISTERED.add(name)

    logger.info(f"Registered tool '{name}'")


def get_tool(name: str):
    """
    Возвращает функцию инструмента.
    """

    tool = TOOLS.get(name)

    if not tool:
        logger.error(f"Tool '{name}' not found")
        return None

    return tool["func"]


def list_tools():
    """
    Возвращает список всех инструментов.
    """

    return list(TOOLS.keys())


async def run_tool(name: str, args: dict):
    """
    Выполняет инструмент.
    Поддерживает async и sync функции.
    """

    tool = TOOLS.get(name)

    if not tool:
        logger.error(f"Tool '{name}' not found")
        return {"error": f"Tool '{name}' not found"}

    func = tool["func"]
    params = tool["params"]

    if args is None:
        args = {}

    # Фильтрация аргументов
    filtered_args = {}

    for k, v in args.items():
        if k in params:
            filtered_args[k] = v
        else:
            logger.warning(f"Ignoring unknown arg '{k}' for tool '{name}'")

    logger.info(f"CALL TOOL {name} {filtered_args}")

    try:

        if asyncio.iscoroutinefunction(func):

            result = await func(**filtered_args)

        else:

            result = func(**filtered_args)

        logger.info(f"TOOL RESULT {result}")

        return result

    except Exception as e:

        logger.error(f"Error running tool '{name}': {e}")

        return {
            "error": str(e)
        }


# 🔥 ОБНОВЛЕНО
def generate_tool_prompt(tool_list=None):
    """
    Генерирует описание инструментов для SYSTEM_PROMPT.
    Если передан tool_list — показывает только выбранные инструменты.
    """

    lines = []

    for name, info in TOOLS.items():

        # 🔥 фильтр
        if tool_list and name not in tool_list:
            continue

        desc = info["description"]
        params = info["params"]

        if params:
            param_text = ", ".join(params)
        else:
            param_text = "no args"

        lines.append(
            f"{name}({param_text}) — {desc}"
        )

    return "\n".join(lines)


# ===========================
# Регистрация инструментов
# ===========================
from .calculator import calculator
from .web_search import web_search
from .web_reader import read_page

register_tool(
    name="calculator",
    description="Вычисляет математическое выражение",
    func=calculator
)

register_tool(
    name="web_search",
    description="Поиск информации в интернете",
    func=web_search
)

register_tool(
    name="read_page",
    description="Чтение текста страницы по URL",
    func=read_page
)