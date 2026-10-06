import secrets
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ToDo, User
from app.schemas import UserCreate
from app.services.auth_service import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.services.todo_service import calculate_remind_times


async def create_telegram_link(
    user: User,
    db: AsyncSession,
) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(UTC) + timedelta(minutes=15)

    user.telegram_link_token = token
    user.telegram_link_expires_at = expires_at

    await db.commit()

    return token

async def get_user_by_email(
    email: str,
    db: AsyncSession,
) -> User | None:
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()

async def register_user(
        user: UserCreate,
        db: AsyncSession
):
    existing_user = await get_user_by_email(user.email, db)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = User(
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)

    await db.commit()
    await db.refresh(new_user)

    return new_user


async def authenticate_user(
        user: UserCreate,
        db: AsyncSession
):
    db_user = await get_user_by_email(user.email, db)

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        {
            "sub": str(db_user.id)
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

async def update_user_timezone(
    user: User,
    timezone: str,
    db: AsyncSession,
) -> User:
    result = await db.execute(
        select(ToDo).where(
            ToDo.user_id == user.id,
            (
                ToDo.morning_remind_at.is_not(None)
                | ToDo.deadline_remind_at.is_not(None)
            ),
        )
    )

    todos = result.scalars().all()

    for todo in todos:
        morning_pending = (
            todo.morning_remind_at is not None
        )
        deadline_pending = (
            todo.deadline_remind_at is not None
        )

        (
            morning_remind_at,
            deadline_remind_at,
        ) = calculate_remind_times(
            todo.target_date,
            todo.deadline_time,
            todo.reminder_type,
            timezone,
        )

        if morning_pending:
            todo.morning_remind_at = morning_remind_at

        if deadline_pending:
            todo.deadline_remind_at = deadline_remind_at

    user.timezone = timezone

    await db.commit()
    await db.refresh(user)

    return user

async def delete_user_account(user: User, db: AsyncSession) -> dict:

    await db.delete(user)
    await db.commit()
    return {"status": "ok", "message": "Аккаунт и все данные успешно удалены."}