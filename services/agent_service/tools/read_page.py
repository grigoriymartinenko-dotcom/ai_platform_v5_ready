# services/agent_service/tools/web_reader.py
import requests
from bs4 import BeautifulSoup

from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("ReadPageTool"), {})

MAX_CHARS = 2000  # Ограничение на длину текста


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
