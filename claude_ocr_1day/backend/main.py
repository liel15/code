from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi.responses import FileResponse

load_dotenv()

app = FastAPI(title="영수증 지출관리 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


FRONTEND_PREVIEW = Path(__file__).resolve().parent.parent / "frontend" / "maratang-memo-ritual.html"


@app.get("/")
def root():
    if FRONTEND_PREVIEW.exists():
        return FileResponse(FRONTEND_PREVIEW, media_type="text/html")
    return {"message": "영수증 지출관리 API 정상 동작 중"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "upstage_api_key_set": bool(os.getenv("UPSTAGE_API_KEY")),
    }
