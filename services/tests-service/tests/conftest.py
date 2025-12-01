"""
Test configuration and fixtures
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.models.db_models import Base
from app.db.session import get_db


SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
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
def sample_user_id():
    """Sample user UUID for testing"""
    from uuid import UUID
    return UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def sample_course_id():
    """Sample course UUID for testing"""
    from uuid import UUID
    return UUID("87654321-4321-8765-4321-876543218765")


@pytest.fixture
def mock_jwt_token(sample_user_id):
    """Mock JWT token for testing"""
    from app.api.dependencies import get_current_user_id
    
    def override_get_current_user_id():
        return sample_user_id
    
    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    
    yield "mock_token"
    
    if get_current_user_id in app.dependency_overrides:
        del app.dependency_overrides[get_current_user_id]

