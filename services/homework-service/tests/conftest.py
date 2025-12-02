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
from app.api.v1 import homeworks
from app.core.config import get_settings


# Create in-memory SQLite database for testing
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
    # Create a test app without lifespan to avoid PostgreSQL connection
    settings = get_settings()
    test_app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Test Homework Service"
    )
    
    # Include routers
    test_app.include_router(homeworks.router, prefix="/api")
    
    # Add health endpoints
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
def teacher_token():
    """Generate a mock teacher JWT token"""
    from jose import jwt
    from datetime import datetime, timedelta
    
    payload = {
        "sub": "12345678-1234-5678-1234-567812345678",
        "email": "teacher@example.com",
        "role": "teacher",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    
    token = jwt.encode(payload, "secret", algorithm="HS256")
    return token


@pytest.fixture
def student_token():
    """Generate a mock student JWT token"""
    from jose import jwt
    from datetime import datetime, timedelta
    
    payload = {
        "sub": "87654321-4321-8765-4321-876543218765",
        "email": "student@example.com",
        "role": "student",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    
    token = jwt.encode(payload, "secret", algorithm="HS256")
    return token


@pytest.fixture
def sample_homework_data():
    """Sample homework data for testing"""
    from datetime import datetime, timedelta
    
    return {
        "title": "Test Homework",
        "description": "This is a test homework assignment",
        "lesson_id": None,
        "due_at": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z",
        "max_score": 10,
        "attachments": ["https://example.com/file.pdf"]
    }


@pytest.fixture
def sample_submission_data():
    """Sample submission data for testing"""
    return {
        "answer_text": "This is my answer",
        "attachments": ["https://example.com/answer.pdf"]
    }

