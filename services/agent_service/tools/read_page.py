# services/agent_service/tools/read_page.py

import httpx
# Правильно для всех инструментов
from services.agent_service.tools.tool_registry import register_tool
from bs4 import BeautifulSoup
from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("ReadPageTool"), {})


def read_page(url: str) -> dict:
    """
    Скачиваем страницу и возвращаем чистый текст
    """
    logger.debug(f"Reading page: {url}")
    try:
        response = httpx.get(url, timeout=5.0)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n")
        # Обрезаем до 5000 символов
        text = text[:5000]
    except Exception as e:
        logger.debug(f"Read page error: {e}")
        text = f"Ошибка при чтении страницы: {e}"

    return {"result": text}
