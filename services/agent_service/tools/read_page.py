# services/agent_service/tools/read_page.py

import httpx
from bs4 import BeautifulSoup

from services.agent_service.tools.tool_registry import register_tool
from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("ReadPageTool"), {})


async def read_page(url: str = "") -> str:
    """
    Скачивает веб-страницу и возвращает очищенный текст.
    """

    logger.debug(f"READ PAGE: {url}")

    if not url:
        return "URL не указан"

    try:

        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url)

        soup = BeautifulSoup(r.text, "html.parser")

        # удаляем скрипты и стили
        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text(separator=" ")

        # ограничение размера
        text = text[:6000]

        return text

    except Exception as e:

        logger.debug(f"READ PAGE ERROR: {e}")

        return f"Ошибка чтения страницы: {e}"


# регистрация инструмента
register_tool(
    "read_page",
    "Read text content from a web page by URL",
    read_page
)
