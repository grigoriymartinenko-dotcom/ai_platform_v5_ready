from fastapi import FastAPI

from services.embedding_service.api.embed import router as embed_router

app = FastAPI(
    title="Embedding Service",
    version="1.0"
)

app.include_router(embed_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready"}
