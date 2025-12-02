"""
Test configuration and fixtures
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.models.db_models import Base
from app.api.v1 import reports
from app.core.config import get_settings


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client with overridden database dependency"""
    settings = get_settings()
    test_app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Test Reports Service"
    )
    
    # Include routers
    test_app.include_router(reports.router, prefix="/api")
    
    # Add health endpoint
    @test_app.get("/health")
    def health_check():
        return {"status": "healthy", "service": settings.APP_NAME}
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    test_app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(test_app) as test_client:
        yield test_client
    
    test_app.dependency_overrides.clear()


@pytest.fixture
def teacher_headers():
    """Headers for teacher authentication"""
    return {
        "x-user-id": "12345678-1234-5678-1234-567812345678",
        "x-user-role": "teacher"
    }


@pytest.fixture
def manager_headers():
    """Headers for manager authentication"""
    return {
        "x-user-id": "22222222-2222-2222-2222-222222222222",
        "x-user-role": "manager"
    }


@pytest.fixture
def admin_headers():
    """Headers for admin authentication"""
    return {
        "x-user-id": "11111111-1111-1111-1111-111111111111",
        "x-user-role": "admin"
    }


@pytest.fixture
def student_headers():
    """Headers for student authentication"""
    return {
        "x-user-id": "87654321-4321-8765-4321-876543218765",
        "x-user-role": "student"
    }


@pytest.fixture
def sample_report_request():
    """Sample report generation request"""
    from datetime import datetime, timedelta, timezone
    
    return {
        "type": "course_performance",
        "format": "xlsx",
        "filters": {
            "course_id": "12345678-1234-5678-1234-567812345678",
            "from": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
            "to": datetime.now(timezone.utc).isoformat()
        }
    }
