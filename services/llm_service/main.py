# services/llm_service/main.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
import os
import asyncio
import time

os.environ["LLAMA_LOG_LEVEL"] = "ERROR"  # убираем лишние логи llama_cpp
from llama_cpp import Llama

from services.utils.logger import get_logger, TraceAdapter

# Логгер
base_logger = get_logger("LLM")
logger = TraceAdapter(base_logger, {})

app = FastAPI(title="LLM Service")
logger.debug("LLM Service started")

# Путь к модели — для теста можно использовать маленькую 3B, для продакшена — 14B
MODEL_PATH = "models/qwen2.5-3b-instruct-q4_k_m.gguf"  # <- ускоренный вариант

# Инициализация Llama
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=8192,
    n_threads=8,
    n_batch=8,
    verbose=False
)

SYSTEM_PROMPT = "Ты дружелюбный и естественный AI-ассистент. Отвечай только на русском языке."


def build_prompt(user_message: str) -> str:
    """Формируем полный prompt для LLM"""
    logger.debug(f"LLM PROMPT: {user_message}")
    return (
        "<|im_start|>system\n"
        f"{SYSTEM_PROMPT}"
        "<|im_end|>\n"
        "<|im_start|>user\n"
        f"{user_message}"
        "<|im_end|>\n"
        "<|im_start|>assistant\n"
    )


async def stream_generate(user_message: str):
    """Стриминг ответа от LLM, выдаём блоками по 50 символов"""
    prompt = build_prompt(user_message)
    logger.debug("LLM STREAM START")
    buffer = ""

    loop = asyncio.get_event_loop()

    # Асинхронный вызов llama_cpp через executor
    def llama_stream():
        return llm(
            prompt,
            max_tokens=512,
            temperature=0.7,
            top_p=0.9,
            stop=["<|im_end|>"],
            stream=True
        )

    for chunk in await loop.run_in_executor(None, llama_stream):
        token = chunk["choices"][0]["text"]
        if not token:
            continue

        buffer += token
        while len(buffer) >= 50:
            to_send = buffer[:50]
            buffer = buffer[50:]
            yield to_send

    if buffer:
        yield buffer


@app.post("/chat_stream")
async def chat_stream(request: Request):
    """Streaming endpoint"""
    data = await request.json()
    user_message = data.get("message", "")

    if not user_message:
        return JSONResponse({"error": "No message"}, status_code=400)

    async def event_stream():
        async for chunk in stream_generate(user_message):
            yield chunk

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/chat")
async def chat(request: Request):
    """Асинхронный endpoint для обычного запроса"""
    start = time.time()
    data = await request.json()
    user_message = data.get("message", "")

    if not user_message:
        return JSONResponse({"error": "No message provided"}, status_code=400)

    prompt = build_prompt(user_message)
    loop = asyncio.get_event_loop()

    # Асинхронный вызов llama_cpp через executor
    def llama_sync():
        return llm(
            prompt,
            max_tokens=512,
            temperature=0.7,
            top_p=0.9,
            stop=["<|im_end|>"]
        )

    output = await loop.run_in_executor(None, llama_sync)
    text = output["choices"][0]["text"].strip()
    latency = round(time.time() - start, 2)
    logger.debug(f"LLM RESPONSE GENERATED ({latency}s)")

    return {"answer": text or "LLM вернул пустой ответ."}


@app.get("/")
async def root():
    return {"status": "LLM Service is running"}
