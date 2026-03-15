# services/agent_service/tools/tavily_search.py

import httpx

from services.agent_service.tools.tool_registry import register_tool
from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("WebSearchTool"), {})

# ⚠️ Вставьте сюда ваши данные из Google Custom Search
GOOGLE_API_KEY = "AIzaSyDjyfb7RCUKMcRKaB4n-LAIlwVr225iaUY"  # "ВАШ_GOOGLE_API_KEY"
SEARCH_ENGINE_ID = "67c056fb8deab42b9"  # "ВАШ_SEARCH_ENGINE_ID"  # cx

API_URL = "https://www.googleapis.com/customsearch/v1"


async def web_search(query: str = "") -> str:
    """
    Ищет в Google Custom Search и возвращает текстовый результат
    """
    logger.debug(f"WEB SEARCH: {query}")
    if not query:
        return "Пустой запрос"

    try:
        params = {
            "key": GOOGLE_API_KEY,
            "cx": SEARCH_ENGINE_ID,
            "q": query,
            "num": 3  # количество результатов
        }

        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(API_URL, params=params)
            r.raise_for_status()
            data = r.json()

        items = data.get("items", [])
        if not items:
            return "Нет данных по запросу."

        # Собираем заголовки + сниппеты
        results = []
        for item in items:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            results.append(f"{title}\n{snippet}\n{link}")

        return "\n\n".join(results)

    except Exception as e:
        logger.debug(f"WEB SEARCH ERROR: {e}")
        return f"Ошибка поиска: {e}"


# Регистрация инструмента
register_tool(
    "web_search",
    "Search the web and return top results from Google",
    web_search
)
