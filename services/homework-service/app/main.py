"""
FastAPI application entry point for Homework Service
"""
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging_config import setup_logging, get_logger
from app.core.metrics import setup_metrics
from app.db.session import init_db
from app.api.v1 import homeworks


settings = get_settings()

# Setup structured logging
setup_logging(
    service_name="homework-service",
    log_level=settings.LOG_LEVEL
)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting up Homework Service", extra={
        "service": "homework-service",
        "version": settings.APP_VERSION,
        "environment": settings.ENV
    })
    init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down Homework Service")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Homework management microservice for online teaching platform",
    lifespan=lifespan
)

# Setup Prometheus metrics
setup_metrics(
    app=app,
    service_name="homework-service",
    service_version=settings.APP_VERSION
)


# Middleware for request logging and tracing
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """
    Middleware to log all HTTP requests with structured logging.
    """
    # Generate request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Log request
    start_time = time.time()
    logger.info(
        "Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_host": request.client.host if request.client else None
        }
    )
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log response
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2)
            }
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    except Exception as e:
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log error
        logger.error(
            f"Request failed: {str(e)}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "duration_ms": round(duration_ms, 2),
                "error": str(e)
            },
            exc_info=True
        )
        
        raise


# Configure CORS
if settings.CORS_ORIGINS:
    origins = settings.CORS_ORIGINS.split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers with /api prefix
app.include_router(homeworks.router, prefix="/api")


@app.get("/", tags=["Health"])
def root():
    """Root endpoint - health check"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "service": settings.APP_NAME
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development
    )

