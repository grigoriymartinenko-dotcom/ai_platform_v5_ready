# read_page.py
import requests
from bs4 import BeautifulSoup

from services.agent_service.tools.tool_registry import register_tool
from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("ReadPageTool"), {})
MAX_CHARS = 2000

def read_page(url: str) -> str:
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        if len(text) > MAX_CHARS:
            logger.info(f"Page too long, truncating to {MAX_CHARS} chars")
            text = text[:MAX_CHARS]
        return text
    except requests.RequestException as e:
        logger.error(f"Failed to read page {url}: {e}")
        return f"Error reading page: {e}"


# 🔹 Регистрируем инструмент
async def read_page_tool(url: str):
    content = read_page(url)
    return {
        "success": True if "Error reading page" not in content else False,
        "data": {"content": content},
        "error": None if "Error reading page" not in content else content
    }


register_tool(
    name="read_page",
    description="Read text content from a web page",
    schema={
        "type": "object",
        "properties": {"url": {"type": "string"}},
        "required": ["url"]
    },
    func=read_page_tool
)
