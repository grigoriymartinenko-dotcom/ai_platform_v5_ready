from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from .pipeline import process_document
from .schemas import DocumentUploadResponse
import shutil
import os

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Document Service", version="v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)


@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    chunks_count = process_document(file_path, file.filename)
    return DocumentUploadResponse(
        filename=file.filename,
        status="processed",
        chunks_created=chunks_count
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}
