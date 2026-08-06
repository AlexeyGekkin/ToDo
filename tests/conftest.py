import pytest
from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi.testclient import TestClient

from app.main import app
from app.database import Base
from app.dependencies import get_db
from app.models import User, ToDo, ReminderType


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)


@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client(db_session):

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    with patch(
        "app.main.bot.get_me",
        new_callable=AsyncMock
    ) as mock_get_me, \
         patch(
             "app.main.dp.start_polling",
             new_callable=AsyncMock
         ), \
         patch(
             "app.main.bot.session.close",
             new_callable=AsyncMock
         ):

        mock_get_me.return_value.username = "test_todo_bot"

        with TestClient(app) as test_client:
            yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session):
    user = User(
        email="test@example.com",
        password="hashed_password_example",
        telegram_id=123456789
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
async def test_todo(db_session, test_user):
    todo = ToDo(
        title="Тестовая задача",
        description="Описание задачи",
        completed=False,
        target_date=None,
        deadline_time=None,
        reminder_type=ReminderType.NONE,
        remind_at=None,
        user_id=test_user.id
    )

    db_session.add(todo)
    await db_session.commit()
    await db_session.refresh(todo)

    return todo