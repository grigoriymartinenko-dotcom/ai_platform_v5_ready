# services/agent_service/planner.py

import re
from services.utils.logger import get_logger, TraceAdapter

base_logger = get_logger("Planner")
logger = TraceAdapter(base_logger, {})
logger.debug("PLANNER start")


def detect_tool(message: str):
    """
    Определяет какой инструмент вызвать.
    Возвращает (tool_name, args) или None
    """

    msg = message.lower().strip()
    logger.debug(f"PLANNER INPUT: {msg}")

    # ------------------------- math
    if re.search(r"[0-9\+\-\*\/]", msg):
        math_expr = "".join(re.findall(r"[0-9\.\+\-\*\/\(\) ]", msg))
        if math_expr:
            logger.debug("PLANNER DETECTED TOOL: math")
            return ("calculator", math_expr)

    # ------------------------- weather
    if "погода" in msg:
        m = re.search(r"погода(?: в)? ([\w\-\s]+)", msg, re.UNICODE)
        city = m.group(1).strip() if m else "киев"
        logger.debug(f"PLANNER DETECTED TOOL: weather ({city})")
        return ("weather", city)

    # ------------------------- web search
    if msg.startswith("найди ") or msg.startswith("поиск "):
        query = msg.replace("найди ", "").replace("поиск ", "").strip()
        logger.debug(f"PLANNER DETECTED TOOL: web_search ({query})")
        return ("web_search", query)

    # ------------------------- read page
    if msg.startswith("прочитай ") or "http" in msg:
        parts = msg.split()
        for p in parts:
            if p.startswith("http"):
                logger.debug(f"PLANNER DETECTED TOOL: web ({p})")
                return ("read_page", p)

    logger.debug("PLANNER: no tool detected")
    return None
