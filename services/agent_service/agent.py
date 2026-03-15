# services/agent_service/agent.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

from services.agent_service.agent_loop import agent_loop
from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("Agent"), {})

app = FastAPI(title="Agent Service")
logger.debug("Agent service starting...")


@app.post("/chat_stream")
async def chat_stream(request: Request):
    """
    Асинхронный streaming endpoint.
    Отдаёт единый диалог: USER → AI
    """
    data = await request.json()
    user_message = data.get("message", "")
    if not user_message:
        return JSONResponse({"error": "No message provided"}, status_code=400)

    async def event_stream():
        # handle_message теперь async
        final_answer, _ = await agent_loop.handle_message(user_message)
        # отдаём весь диалог как один кусок, без лишних меток
        yield final_answer

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/chat")
async def chat(request: Request):
    """
    Асинхронный endpoint для обычного запроса.
    Возвращает JSON с диалогом.
    """
    data = await request.json()
    user_message = data.get("message", "")
    if not user_message:
        return JSONResponse({"error": "No message provided"}, status_code=400)

    final_answer, _ = await agent_loop.handle_message(user_message)

    return {
        "answer": final_answer
    }


@app.get("/")
async def root():
    return {"status": "Agent Service is running"}
