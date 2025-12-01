"""
Test configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db
from app.models.db_models import Base


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
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def teacher_headers():
    """Headers for teacher authentication"""
    return {
        "x-user-id": "12345678-1234-5678-1234-567812345678",
        "x-user-role": "teacher"
    }


@pytest.fixture
def student_headers():
    """Headers for student authentication"""
    return {
        "x-user-id": "87654321-4321-8765-4321-876543218765",
        "x-user-role": "student"
    }


@pytest.fixture
def admin_headers():
    """Headers for admin authentication"""
    return {
        "x-user-id": "11111111-1111-1111-1111-111111111111",
        "x-user-role": "admin"
    }


@pytest.fixture
def sample_lesson_data():
    """Sample lesson data for testing"""
    from datetime import datetime, timedelta
    
    start = datetime.utcnow() + timedelta(days=1)
    end = start + timedelta(hours=1)
    
    return {
        "title": "Test Lesson",
        "description": "This is a test lesson",
        "start_at": start.isoformat() + "Z",
        "end_at": end.isoformat() + "Z",
        "location_type": "online",
        "online_link": "https://meet.example.com/test",
        "room": None
    }


@pytest.fixture
def sample_attendance_data():
    """Sample attendance data for testing"""
    return {
        "items": [
            {
                "student_id": "87654321-4321-8765-4321-876543218765",
                "status": "present",
                "comment": None
            },
            {
                "student_id": "99999999-9999-9999-9999-999999999999",
                "status": "absent",
                "comment": "Was sick"
            }
        ]
    }

