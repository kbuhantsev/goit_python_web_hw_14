import asyncio
from pathlib import Path
import sys
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
import pytest
from redis import Redis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

curr_path = Path(__file__).resolve().parent
hw_path: str = str(curr_path.parent)
sys.path.append(str(hw_path))

from main import app
from src.database.db import get_db
from src.database.models import Base


DATABASE_TEST_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_TEST_URL)

TestingSession = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


@pytest.fixture()
def mock_ratelimiter(monkeypatch):
    mock_rate_limiter = AsyncMock()
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", mock_rate_limiter)
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", mock_rate_limiter)
    monkeypatch.setattr(
        "fastapi_limiter.FastAPILimiter.http_callback", mock_rate_limiter
    )

    redis = AsyncMock(spec=Redis)
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=None)
    redis.expire = AsyncMock(return_value=None)

    monkeypatch.setattr("src.services.auth.auth_service.r", redis)


@pytest.fixture(scope="module")
def user():
    return {
        "name": "test",
        "email": "test@test.com",
        "password": "testtest",
        "avatar": None,
        "role": "USER",
    }


@pytest.fixture(scope="module")
def contact():
    result = {
        "name": "test",
        "surname": "test",
        "email": "test@example.com",
        "phone": "+380000000000",
        "date_of_birth": "2022-07-07",
        "id": 1,
    }
    return result


@pytest.fixture(scope="module")
def session():

    async def get_session():
        async with TestingSession() as session:
            yield session

    asyncio.run(get_session())


@pytest.fixture(scope="module", autouse=True)
def create_test_database():
    async def init():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init())


@pytest.fixture(scope="module")
def client():

    async def override_get_db():
        async with TestingSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)
