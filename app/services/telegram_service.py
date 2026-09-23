from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, ToDo
from app.services.todo_service import calculate_remind_times


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


async def get_webapp_todos(
    telegram_id: int,
    db: AsyncSession
):
    user = await get_user_by_telegram_id(
        telegram_id,
        db
    )

    result = await db.execute(
        select(ToDo).where(
            ToDo.user_id == user.id
        )
    )

    return result.scalars().all()


async def create_webapp_todo(
    telegram_id: int,
    data,
    db: AsyncSession
):
    user = await get_user_by_telegram_id(
        telegram_id,
        db
    )

    (
        morning_remind_at,
        deadline_remind_at
    ) = calculate_remind_times(
        data.target_date,
        data.deadline_time,
        data.reminder_type
    )

    todo = ToDo(
        title=data.title,
        description=data.description,
        target_date=data.target_date,
        deadline_time=data.deadline_time,
        morning_remind_at=morning_remind_at,
        deadline_remind_at=deadline_remind_at,
        reminder_type=data.reminder_type,
        user_id=user.id,
    )

    db.add(todo)

    await db.commit()
    await db.refresh(todo)

    return {
        "status": "ok",
        "id": todo.id
    }


async def update_webapp_todo(
    telegram_id: int,
    todo_id: int,
    completed: bool,
    db: AsyncSession
):
    result = await db.execute(
        select(ToDo)
        .join(User)
        .where(
            ToDo.id == todo_id,
            User.telegram_id == telegram_id
        )
    )

    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    todo.completed = completed

    await db.commit()

    return {
        "status": "ok"
    }


async def delete_webapp_account(
    telegram_id: int,
    db: AsyncSession
):
    user = await get_user_by_telegram_id(
        telegram_id,
        db
    )

    await db.delete(user)

    await db.commit()

    return {
        "status": "ok",
        "message": "Account deleted"
    }
