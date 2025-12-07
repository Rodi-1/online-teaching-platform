"""
Main application module for Tests Service
"""
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import tests
from app.core.config import get_settings
from app.core.logging_config import setup_logging, get_logger
from app.core.metrics import setup_metrics
from app.db.session import init_db


settings = get_settings()

# Setup structured logging
setup_logging(
    service_name="tests-service",
    log_level=settings.LOG_LEVEL
)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    logger.info("Starting Tests Service", extra={
        "service": "tests-service",
        "version": settings.APP_VERSION,
        "environment": settings.ENV
    })
    
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise
    
    yield
    
    logger.info("Shutting down Tests Service")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Tests Service API",
    lifespan=lifespan
)

# Setup Prometheus metrics
instrumentator = setup_metrics(
    app=app,
    service_name="tests-service",
    service_version=settings.APP_VERSION
)


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


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tests.router, prefix="/api", tags=["tests"])

@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {"status": "healthy", "service": settings.APP_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.is_development)
