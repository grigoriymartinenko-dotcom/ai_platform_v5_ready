# services/gateway_service/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

# Загрузка настроек из .env
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://localhost:8100")
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://localhost:8200")
DOCUMENT_SERVICE_URL = os.getenv("DOCUMENT_SERVICE_URL", "http://localhost:8300")
MATH_SERVICE_URL = os.getenv("MATH_SERVICE_URL", "http://localhost:8400")

app = FastAPI(title="Gateway Service")

# Разрешаем CORS для frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# Проверка доступности всех сервисов
async def check_service(url: str):
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{url}/health")
            if resp.status_code == 200:
                return True
    except Exception:
        return False
    return False


async def check_all_services():
    services = {
        "LLM Service": LLM_SERVICE_URL,
        "RAG Service": RAG_SERVICE_URL,
        "Document Service": DOCUMENT_SERVICE_URL,
        "Math Service": MATH_SERVICE_URL,
    }
    unavailable = []
    for name, url in services.items():
        ok = await check_service(url)
        if not ok:
            unavailable.append(f"{name} ({url})")
    return unavailable


@app.get("/health")
async def health():
    unavailable = await check_all_services()
    if unavailable:
        return {"status": "error", "unavailable_services": unavailable}
    return {"status": "ok"}


# Пример маршрута для chat с LLM
@app.post("/chat")
async def chat(request: dict):
    unavailable = await check_all_services()
    if unavailable:
        raise HTTPException(status_code=503, detail={
            "error": "Some services are unavailable",
            "services": unavailable
        })
    # Отправляем запрос к LLM Service
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{LLM_SERVICE_URL}/chat", json=request)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Пример маршрута для RAG
@app.post("/rag")
async def rag(request: dict):
    unavailable = await check_all_services()
    if unavailable:
        raise HTTPException(status_code=503, detail={
            "error": "Some services are unavailable",
            "services": unavailable
        })
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{RAG_SERVICE_URL}/query", json=request)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Пример маршрута для Document Service
@app.post("/document")
async def document(request: dict):
    unavailable = await check_all_services()
    if unavailable:
        raise HTTPException(status_code=503, detail={
            "error": "Some services are unavailable",
            "services": unavailable
        })
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(f"{DOCUMENT_SERVICE_URL}/process", json=request)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Пример маршрута для Math Service
@app.post("/math")
async def math(request: dict):
    unavailable = await check_all_services()
    if unavailable:
        raise HTTPException(status_code=503, detail={
            "error": "Some services are unavailable",
            "services": unavailable
        })
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(f"{MATH_SERVICE_URL}/compute", json=request)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
