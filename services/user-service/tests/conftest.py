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
from app.api.v1 import auth, users
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
        description="Test User Service"
    )
    
    # Include routers
    test_app.include_router(auth.router, prefix="/api")
    test_app.include_router(users.router, prefix="/api")
    
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
def test_user_data():
    """Test user registration data"""
    return {
        "email": "test@example.com",
        "phone": "+79990001122",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "role": "student"
    }


@pytest.fixture
def admin_user_data():
    """Test admin user registration data"""
    return {
        "email": "admin@example.com",
        "phone": "+79990001133",
        "password": "adminpassword123",
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin"
    }

