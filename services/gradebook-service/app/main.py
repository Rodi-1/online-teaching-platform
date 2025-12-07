"""FastAPI application entry point for Gradebook Service"""
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging_config import setup_logging, get_logger
from app.core.metrics import setup_metrics
from app.db.session import init_db
from app.api.v1 import gradebook

settings = get_settings()

# Setup structured logging
setup_logging(
    service_name="gradebook-service",
    log_level=settings.LOG_LEVEL
)
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Gradebook Service", extra={
        "service": "gradebook-service",
        "version": settings.APP_VERSION,
        "environment": settings.ENV
    })
    init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down Gradebook Service")

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

# Setup Prometheus metrics
instrumentator = setup_metrics(
    app=app,
    service_name="gradebook-service",
    service_version=settings.APP_VERSION
)

# Expose metrics endpoint
metrics_app = instrumentator.expose(app, endpoint="/metrics", include_in_schema=False)

# Middleware for request logging and tracing
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Middleware to log all HTTP requests with structured logging."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    logger.info("Request started", extra={
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "client_host": request.client.host if request.client else None
    })
    
    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        
        logger.info("Request completed", extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2)
        })
        
        response.headers["X-Request-ID"] = request_id
        return response
    
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"Request failed: {str(e)}", extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "duration_ms": round(duration_ms, 2),
            "error": str(e)
        }, exc_info=True)
        raise

if settings.CORS_ORIGINS:
    app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS.split(","),
                      allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(gradebook.router, prefix="/api")

@app.get("/", tags=["Health"])
def root():
    return {"service": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}

@app.get("/health", tags=["Health"])
def health():
    logger.debug("Health check requested")
    return {"status": "healthy", "service": settings.APP_NAME}
