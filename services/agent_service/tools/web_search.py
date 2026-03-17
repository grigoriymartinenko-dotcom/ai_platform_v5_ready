# services/agent_service/tools/web_search.py

import re
import httpx

from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("WebSearchTool"), {})

TAVILY_API_KEY = "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"
TAVILY_URL = "https://api.tavily.com/search"


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"<.*?>", "", text)
    return text.strip()


def build_summary(results):
    texts = []

    for r in results[:5]:

        # 🔥 берём ВСЁ возможное
        content = r.get("content") or ""
        snippet = r.get("snippet") or ""

        text = content if len(content) > len(snippet) else snippet
        text = clean_text(text)

        if text:
            texts.append(text)

    if not texts:
        return "No useful data found"

    return " ".join(texts[:5])


async def web_search(query: str = "") -> str:

    if not query:
        return "Empty query"

    headers = {
        "Authorization": f"Bearer {TAVILY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": query,
        "limit": 5
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(TAVILY_URL, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            if not results:
                return f"Нет данных по запросу: {query}"

            summary = build_summary(results)

            # 🔥 fallback если Tavily дал мусор
            if "No useful data" in summary or len(summary) < 20:
                return f"Не удалось получить точные данные по запросу: {query}"

            logger.info(f"WEB SUMMARY: {summary[:200]}")

            return summary

    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return f"Ошибка поиска: {e}"