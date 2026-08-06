import pytest_asyncio

from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

from sqlalchemy.pool import StaticPool

from app.app_factory import create_app
from app.database import Base
from app.dependencies import get_db


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

app = create_app(with_bot=False)


@pytest_asyncio.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def auth_token(client):
    payload = {
        "email": "test@example.com",
        "password": "12345678"
    }

    await client.post(
        "/users/register",
        json=payload,
    )

    response = await client.post(
        "/users/login",
        json=payload,
    )

    return response.json()["access_token"]

@pytest_asyncio.fixture
async def second_auth_token(client):
    payload = {
        "email": "second@example.com",
        "password": "12345678"
    }

    await client.post(
        "/users/register",
        json=payload,
    )

    response = await client.post(
        "/users/login",
        json=payload,
    )

    return response.json()["access_token"]