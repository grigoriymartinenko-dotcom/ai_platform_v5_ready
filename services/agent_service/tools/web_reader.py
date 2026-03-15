# services/agent_service/tools/web_reader.py

import httpx
from bs4 import BeautifulSoup

from services.agent_service.tools.tool_registry import register_tool
from services.utils.logger import get_logger, TraceAdapter

base_logger = get_logger("WebReader")
logger = TraceAdapter(base_logger, {})


async def read_page(url: str = ""):

    logger.info(f"READ PAGE {url}")

    try:

        async with httpx.AsyncClient(timeout=15) as client:

            r = await client.get(url)

        soup = BeautifulSoup(r.text, "html.parser")

        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text(separator=" ")

        return text[:6000]

    except Exception as e:

        return f"Ошибка чтения страницы: {e}"


register_tool(
    "web_reader",
    "Read text content from web page",
    read_page
)