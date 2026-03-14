# services/agent_service/agent_stream.py

import httpx
from services.utils.logger import get_logger, TraceAdapter

base_logger = get_logger("AgentStream")
logger = TraceAdapter(base_logger, {})

LLM_URL = "http://localhost:8100/chat_stream"


async def stream_llm(message: str):
    """
    Получаем stream от LLM и отправляем SSE chunks
    """

    logger.debug(f"STREAM LLM START message={message}")

    buffer = ""

    try:

        async with httpx.AsyncClient(timeout=None) as client:

            async with client.stream(
                    "POST",
                    LLM_URL,
                    json={"message": message}
            ) as r:

                logger.debug(f"LLM STREAM CONNECTED status={r.status_code}")

                async for chunk in r.aiter_bytes():

                    if not chunk:
                        continue

                    text = chunk.decode("utf-8", errors="ignore")

                    buffer += text

                    while len(buffer) >= 50:
                        part = buffer[:50]
                        buffer = buffer[50:]

                        logger.debug(f"STREAM CHUNK: {part}")

                        yield f" {part}\n\n"

                if buffer:
                    logger.debug(f"STREAM FINAL CHUNK: {buffer}")
                    yield f"{buffer}\n\n"

        logger.debug("LLM STREAM FINISHED")

    except httpx.RemoteProtocolError:

        logger.warning("LLM STREAM CLOSED BY REMOTE")

    except Exception as e:

        logger.error(f"STREAM ERROR {e}")

        yield f"Agent error: {str(e)}\n\n"


async def stream_text(text: str):
    """
    Стримим обычный текст (например ответ tool)
    """

    logger.debug(f"STREAM TOOL TEXT size={len(text)}")

    for i in range(0, len(text), 50):
        part = text[i:i + 50]

        logger.debug(f"STREAM TOOL CHUNK: {part}")

        yield f"data: {part}\n\n"
