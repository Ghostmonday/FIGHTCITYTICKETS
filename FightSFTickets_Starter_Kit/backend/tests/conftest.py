"""
Pytest configuration and fixtures for FightSFTickets tests.
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test environment before importing app
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://postgres:postgres@localhost:5432/fightsf_test"
)

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import app
from src.models import Base
from src.services.database import DatabaseService


@pytest.fixture(scope="function")
def test_db():
    """
    Create a test database and yield a session.

    This fixture creates a fresh database for each test and cleans up afterward.
    """
    # Create test database engine - use SQLite for testing without Docker
    test_db_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False} if "sqlite" in test_db_url else {},
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def client():
    """
    Create a test client for the FastAPI application.
    """
    return TestClient(app)


@pytest.fixture(scope="function")
def mock_stripe_service(monkeypatch):
    """
    Mock Stripe service for testing.
    """

    class MockStripeService:
        def verify_webhook_signature(self, payload, signature):
            return True

        def create_checkout_session(self, request):
            return {
                "checkout_url": "https://checkout.stripe.com/test",
                "session_id": "cs_test_123",
                "amount_total": 989,
                "currency": "usd",
            }

    from src.services import stripe_service

    monkeypatch.setattr(stripe_service, "StripeService", MockStripeService)
    return MockStripeService()
