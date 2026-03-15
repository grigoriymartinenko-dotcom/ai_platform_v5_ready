import httpx

from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("WebSearchTool"), {})

TAVILY_API_KEY = "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"


async def web_search(query: str = ""):
    logger.debug(f"WEB SEARCH: {query}")

    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "basic",
        "max_results": 5
    }

    try:

        async with httpx.AsyncClient(timeout=30) as client:

            r = await client.post(
                "https://api.tavily.com/search",
                json=payload
            )

        data = r.json()

    except Exception as e:

        logger.debug(f"WEB SEARCH ERROR: {e}")
        return f"Search error: {e}"

    results = []

    for item in data.get("results", []):
        title = item.get("title", "")
        content = item.get("content", "")
        url = item.get("url", "")

        results.append(
            f"{title}\n{content}\n{url}"
        )

    return "\n\n".join(results)
