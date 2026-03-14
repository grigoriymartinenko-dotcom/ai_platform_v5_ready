# services/agent_service/tools/web_search.py

import httpx
# Правильно для всех инструментов
from services.agent_service.tools.tool_registry import register_tool
from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("WebSearchTool"), {})


def web_search(query: str) -> dict:
    """
    Простой поиск в интернете через DuckDuckGo Instant API
    """
    logger.debug(f"Web search query: {query}")
    url = "https://api.duckduckgo.com/"
    params = {"q": query, "format": "json", "no_redirect": 1}

    try:
        response = httpx.get(url, params=params, timeout=5.0)
        data = response.json()
        answer = data.get("AbstractText") or "Нет данных по запросу."
    except Exception as e:
        logger.debug(f"Web search error: {e}")
        answer = f"Ошибка поиска: {e}"

    return {"result": answer}
