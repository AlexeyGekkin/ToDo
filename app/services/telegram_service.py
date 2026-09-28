from fastapi import HTTPException
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, ToDo


async def get_user_by_telegram_id(
    telegram_id: int,
    db: AsyncSession
) -> User:
    result = await db.execute(
        select(User).where(
            User.telegram_id == telegram_id
        )
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


async def get_profile(
    telegram_id: int,
    db: AsyncSession
):
    user = await get_user_by_telegram_id(
        telegram_id,
        db
    )

    stmt = (
        select(
            func.count(ToDo.id),
            func.count(ToDo.id).filter(
                ToDo.completed == False
            )
        )
        .where(
            ToDo.user_id == user.id
        )
    )

    res = await db.execute(stmt)
    total, active = res.tuple()

    return {
        "email": user.email,
        "active_count": active,
        "completed_count": total - active,
    }


async def delete_webapp_account(
    telegram_id: int,
    db: AsyncSession,
):
    result = await db.execute(
        select(User.id)
        .where(User.telegram_id == telegram_id)
    )

    user_id = result.scalar_one_or_none()

    if user_id is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    await db.execute(
        delete(ToDo).where(
            ToDo.user_id == user_id
        )
    )

    await db.execute(
        delete(User).where(
            User.id == user_id
        )
    )

    await db.commit()

    return {
        "status": "ok",
        "message": "Account deleted",
    }