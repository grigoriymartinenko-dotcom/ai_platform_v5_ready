# services/gateway_service/main.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
import httpx

from services.utils.logger import get_logger, new_trace, TraceAdapter

base_logger = get_logger("Gateway")
logger = TraceAdapter(base_logger, {})

app = FastAPI(title="Gateway Service")

logger.debug("GATEWAY Service started")

AGENT_URL = "http://localhost:8500/chat"
AGENT_STREAM_URL = "http://localhost:8500/chat_stream"


@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("message")

    trace_id = new_trace()
    log = TraceAdapter(base_logger, {"trace_id": trace_id})

    log.info(f"GATEWAY MESSAGE(chat): {message}")

    if not message:
        return JSONResponse({"error": "No message"}, status_code=400)

    try:

        async with httpx.AsyncClient(timeout=120) as client:

            r = await client.post(
                AGENT_URL,
                json={"message": message}
            )

            r.raise_for_status()

            data = r.json()

            return JSONResponse(data)

    except Exception as e:

        log.error(f"GATEWAY ERROR: {e}")

        return JSONResponse(
            {"answer": f"Gateway error: {str(e)}"},
            status_code=500
        )


@app.post("/chat_stream")
async def chat_stream(request: Request):
    body = await request.json()
    message = body.get("message")

    trace_id = new_trace()
    log = TraceAdapter(base_logger, {"trace_id": trace_id})

    log.info(f"GATEWAY MESSAGE(chat_stream): {message}")

    if not message:
        return JSONResponse({"error": "No message"}, status_code=400)

    async def stream():

        try:

            async with httpx.AsyncClient(timeout=None) as client:

                async with client.stream(
                        "POST",
                        AGENT_STREAM_URL,
                        json={"message": message}
                ) as r:

                    async for chunk in r.aiter_text():

                        if chunk:
                            yield chunk

        except httpx.RemoteProtocolError:

            log.warning("STREAM CLOSED BY AGENT")

        except Exception as e:

            log.error(f"STREAM ERROR: {e}")

            yield f"data: Gateway stream error: {str(e)}\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream"
    )
