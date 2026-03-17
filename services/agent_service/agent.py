# services/agent_service/agent.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import httpx

from services.agent_service.agent_loop import agent_loop
from services.agent_service.planner import create_plan
from services.agent_service.prompt import FINAL_PROMPT
from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("Agent"), {})

app = FastAPI(title="Agent Service")

LLM_URL = "http://localhost:8100/chat"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def final_synthesis(results_text: str):

    prompt = FINAL_PROMPT + "\n" + results_text

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(LLM_URL, json={"message": prompt})

        if r.status_code != 200:
            return results_text

        return r.json().get("answer", results_text)


@app.post("/chat")
async def chat(request: Request):

    data = await request.json()
    user_message = data.get("message", "")

    if not user_message:
        return JSONResponse({"error": "No message provided"}, status_code=400)

    # 1. PLAN
    steps = await create_plan(user_message)
    if not steps:
        steps = [user_message]

    # 2. EXECUTE
    results = []

    for step in steps:
        result = await agent_loop.execute_step(step)
        results.append(result)

    results_text = "\n\n".join(results)

    # 🔥 3. FINAL SYNTHESIS
    final_answer = await final_synthesis(results_text)

    return {"answer": final_answer}


@app.post("/chat_stream")
async def chat_stream(request: Request):

    data = await request.json()
    user_message = data.get("message", "")

    async def event_stream():

        steps = await create_plan(user_message)
        if not steps:
            steps = [user_message]

        results = []

        for step in steps:
            result = await agent_loop.execute_step(step)
            results.append(result)

        results_text = "\n\n".join(results)

        final_answer = await final_synthesis(results_text)

        yield final_answer

    return StreamingResponse(event_stream(), media_type="text/event-stream")