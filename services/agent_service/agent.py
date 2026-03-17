# services/agent_service/agent.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from services.agent_service.agent_loop import agent_loop
from services.utils.logger import get_logger, TraceAdapter


logger = TraceAdapter(get_logger("Agent"), {})

app = FastAPI(title="Agent Service")

logger.debug("Agent service starting...")


# CORS (нужно для фронта на localhost:3000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для разработки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

        final_answer, _ = await agent_loop.handle_message(user_message)

        yield final_answer

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )


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