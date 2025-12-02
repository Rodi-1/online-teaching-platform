"""Test configuration"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.models.db_models import Base
from app.api.v1 import gradebook
from app.core.config import get_settings


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
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
        description="Test Gradebook Service"
    )
    
    # Include routers
    test_app.include_router(gradebook.router, prefix="/api")
    
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
def teacher_token():
    from jose import jwt
    from datetime import datetime, timedelta
    payload = {"sub": "12345678-1234-5678-1234-567812345678", "email": "teacher@example.com",
               "role": "teacher", "exp": datetime.utcnow() + timedelta(hours=1)}
    return jwt.encode(payload, "secret", algorithm="HS256")
