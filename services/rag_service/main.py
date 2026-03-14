from fastapi import FastAPI

from services.rag_service.api.ingest import router as ingest_router
from services.rag_service.api.search import router as search_router

app = FastAPI(
    title="RAG Service",
    version="1.0"
)

app.include_router(ingest_router)
app.include_router(search_router)


@app.get("/health")
def health():
    return {"status": "ok"}
