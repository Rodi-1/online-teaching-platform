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
from app.api.v1 import profile
from app.core.config import get_settings


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database dependency"""
    settings = get_settings()
    test_app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Test Profile Service"
    )
    
    # Include routers (same prefix as in main.py)
    test_app.include_router(profile.router, prefix="/api/profile")
    
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
def sample_user_id():
    """Sample user UUID for testing"""
    from uuid import UUID
    return UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def mock_jwt_token(sample_user_id, client):
    """Mock JWT token for testing"""
    from app.api.dependencies import get_current_user_id
    
    def override_get_current_user_id():
        return sample_user_id
    
    # Get the test_app from client fixture
    client.app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    
    yield "mock_token"
    
    if get_current_user_id in client.app.dependency_overrides:
        del client.app.dependency_overrides[get_current_user_id]
