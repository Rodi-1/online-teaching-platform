"""FastAPI application entry point"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.db.session import init_db
from app.api.v1 import gradebook

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Gradebook Service...")
    init_db()
    print("Database initialized")
    yield
    print("Shutting down Gradebook Service...")

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

if settings.CORS_ORIGINS:
    app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS.split(","),
                      allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(gradebook.router, prefix="/api")

@app.get("/", tags=["Health"])
def root():
    return {"service": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "service": settings.APP_NAME}

