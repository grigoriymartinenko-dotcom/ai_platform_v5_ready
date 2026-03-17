# services/agent_service/agent.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import httpx
import json
from sympy import sympify
import re

from services.agent_service.agent_loop import agent_loop, ExecutionContext
from services.agent_service.planner import create_plan
from services.agent_service.prompt import FINAL_PROMPT
from services.agent_service.tools.tool_registry import run_tool
from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("Agent"), {})

app = FastAPI(title="Agent Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LLM_URL = "http://localhost:8100/chat"

# 🔹 Встроенный инструмент для решения необходимости куртки
async def evaluate_jacket_need(args: dict):
    temp = None
    if "weather" in args:
        m = re.search(r"Температура:\s*([\d\.\-]+)°C", args["weather"])
        if m:
            temp = float(m[1])
    expr_result = args.get("expression_result", 0)

    if temp is not None:
        if temp < 10 or expr_result > 50:
            return "Рекомендую взять куртку."
        else:
            return "Куртка, скорее всего, не нужна."
    return "Недостаточно данных для решения."

async def final_synthesis(results_text: str):
    """Финальный синтез ответа через LLM"""
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

    steps = await create_plan(user_message)
    if not steps:
        steps = [user_message]

    result = await agent_loop.execute(user_message, steps)
    final_answer = await final_synthesis(result)

    return {"answer": final_answer}


@app.post("/chat_stream")
async def chat_stream(request: Request):
    data = await request.json()
    user_message = data.get("message", "")

    async def event_stream():
        steps = await create_plan(user_message)
        if not steps:
            steps = [user_message]

        context = ExecutionContext(user_message, steps)

        for step_index, step_text in enumerate(steps):
            yield f"event: step\n"
            yield f"data: {json.dumps({'step_index': step_index, 'step': step_text}, ensure_ascii=False)}\n\n"

            await agent_loop.think(context, step_text)
            thought = context.thoughts[-1] if context.thoughts else ""
            yield f"event: think\n"
            yield f"data: {json.dumps({'step_index': step_index, 'thought': thought}, ensure_ascii=False)}\n\n"

            actions = await agent_loop.act(context, step_text)
            yield f"event: act\n"
            yield f"data: {json.dumps({'step_index': step_index, 'actions': actions}, ensure_ascii=False)}\n\n"

            for action in actions:
                if action["type"] == "tool":
                    tool_name = action["tool"]
                    args = action.get("args", {})

                    # 🔹 Автоопределение инструмента
                    auto_substituted = False
                    if tool_name == "tool":
                        if "expression_result" in args and "weather" in args:
                            tool_name = "evaluate_jacket_need"
                            auto_substituted = True
                        elif "expression" in args:
                            tool_name = "calculator"
                            auto_substituted = True
                        elif "city" in args:
                            tool_name = "weather"
                            auto_substituted = True
                        else:
                            result = f"Unknown tool for action: {action}"
                            context.add_step(step_text, "tool", args, result)
                            yield f"event: tool_result\n"
                            yield f"data: {json.dumps({'step_index': step_index, 'tool': tool_name, 'result': result}, ensure_ascii=False)}\n\n"
                            continue

                    if auto_substituted:
                        logger.info(f"Auto-substituted tool '{tool_name}' for action: {action}")

                    if "expression" in args and isinstance(args["expression"], str):
                        args["expression"] = args["expression"].replace("%", "/100")

                    try:
                        if tool_name == "calculator" and "expression" in args:
                            result = str(sympify(args["expression"]).evalf())
                        elif tool_name == "evaluate_jacket_need":
                            result = await evaluate_jacket_need(args)
                        else:
                            result = await run_tool(tool_name, args)
                    except Exception as e:
                        result = f"Tool error: {e}"

                    context.add_step(step_text, "tool", args, result)
                    yield f"event: tool_result\n"
                    yield f"data: {json.dumps({'step_index': step_index, 'tool': tool_name, 'result': result}, ensure_ascii=False)}\n\n"

        results_text = "\n\n".join([
            s['result'] for s in context.step_results
            if isinstance(s['result'], str) and s['result'].strip()
        ])
        final_answer = await final_synthesis(results_text)

        yield f"event: done\n"
        yield f"data: {json.dumps({'final_answer': final_answer}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")