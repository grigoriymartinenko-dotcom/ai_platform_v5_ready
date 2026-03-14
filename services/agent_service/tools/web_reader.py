# services/agent_service/tools/web_reader.py

import httpx
from bs4 import BeautifulSoup

# Правильно для всех инструментов
from services.agent_service.tools.tool_registry import register_tool
from services.utils.logger import get_logger, TraceAdapter

base_logger = get_logger("WebReader")
logger = TraceAdapter(base_logger, {})


async def read_page(url: str):
    logger.info(f"READ PAGE {url}")

    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=15)

    soup = BeautifulSoup(r.text, "html.parser")

    text = soup.get_text()

    return text[:5000]


register_tool(
    "read_page",
    "Read text from web page",
    read_page
)
