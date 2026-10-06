import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.models import ToDo, User
from app.services.telegram_service import (
    get_profile,
    get_user_by_telegram_id, delete_webapp_account,
)

@pytest.mark.asyncio
async def test_get_user_by_telegram_id(db_session):
    user = User(
        email="telegram@example.com",
        password="hashed_password",
        telegram_id=123456,
    )

    db_session.add(user)
    await db_session.commit()

    result = await get_user_by_telegram_id(
        123456,
        db_session,
    )

    assert result.id == user.id
    assert result.telegram_id == 123456

@pytest.mark.asyncio
async def test_get_user_by_telegram_id_not_found(db_session):
    with pytest.raises(HTTPException) as exc:
        await get_user_by_telegram_id(
            999999,
            db_session,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "User not found"

@pytest.mark.asyncio
async def test_get_profile(db_session):
    user = User(
        email="profile@example.com",
        password="hashed_password",
        telegram_id=123456,
    )

    db_session.add(user)
    await db_session.flush()

    db_session.add_all([
        ToDo(
            title="Active 1",
            completed=False,
            user_id=user.id,
        ),
        ToDo(
            title="Active 2",
            completed=False,
            user_id=user.id,
        ),
        ToDo(
            title="Completed",
            completed=True,
            user_id=user.id,
        ),
    ])

    await db_session.commit()

    result = await get_profile(
        123456,
        db_session,
    )

    assert result == {
        "email": "profile@example.com",
        "active_count": 2,
        "completed_count": 1,
    }

@pytest.mark.asyncio
async def test_delete_webapp_account(db_session):
    user = User(
        email="delete@example.com",
        password="hashed_password",
        telegram_id=123456,
    )

    db_session.add(user)
    await db_session.flush()

    todo = ToDo(
        title="Delete me",
        user_id=user.id,
    )

    db_session.add(todo)
    await db_session.commit()

    result = await delete_webapp_account(
        123456,
        db_session,
    )

    assert result == {
        "status": "ok",
        "message": "Account deleted",
    }

    user_result = await db_session.execute(
        select(User).where(User.id == user.id)
    )

    todo_result = await db_session.execute(
        select(ToDo).where(ToDo.id == todo.id)
    )

    assert user_result.scalar_one_or_none() is None
    assert todo_result.scalar_one_or_none() is None