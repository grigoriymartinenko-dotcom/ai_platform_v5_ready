# web_search.py
# ------------------------
import httpx

from services.agent_service.tools.tool_registry import register_tool

API_KEY = "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"


async def web_search(query: str = ""):
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post("https://api.tavily.com/search", json={"api_key": API_KEY, "query": query})
            data = r.json()
        return {"success": True, "data": {"results": data.get("results", [])}, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


register_tool(
    name="web_search",
    description="Search the web",
    schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
    func=web_search
)
