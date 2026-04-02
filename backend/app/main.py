import logging
import os

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import documents, podcasts, providers, publish
from app.api.websocket import router as ws_router
from app.config import settings
from app.models.database import init_db

app = FastAPI(title="Podcast Generator", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(podcasts.router)
app.include_router(providers.router)
app.include_router(publish.router)
app.include_router(ws_router)


@app.on_event("startup")
async def startup():
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.output_dir, exist_ok=True)
    await init_db()


@app.get("/api/health")
async def health():
    return {"status": "ok"}
