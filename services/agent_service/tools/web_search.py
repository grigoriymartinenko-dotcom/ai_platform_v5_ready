# services/agent_service/tools/web_search.py
import re

import httpx

from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("WebSearchTool"), {})

TAVILY_API_KEY = "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"
TAVILY_URL = "https://api.tavily.com/search"  # Проверь документацию Tavily


def clean_text(text: str) -> str:
    """Чистит текст от HTML и лишних пробелов"""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"<.*?>", "", text)
    return text.strip()


async def web_search(query: str = "") -> str:
    if not query:
        return "Empty query"

    headers = {
        "Authorization": f"Bearer {TAVILY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"query": query, "limit": 5}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(TAVILY_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            if not results:
                return "No results found"
            # Форматируем заголовки и ссылки
            formatted_results = []
            for r in results:
                title = clean_text(r.get("title", "No title"))
                snippet = clean_text(r.get("snippet", ""))
                url = r.get("url", "")
                formatted_results.append(f"{title}: {snippet} ({url})")
            return "\n\n".join(formatted_results)
    except httpx.HTTPError as e:
        logger.error(f"Web search failed: {e}")
        return f"Error: {e}"
