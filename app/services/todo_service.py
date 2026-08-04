from datetime import datetime, time
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc, desc

from app.models.todo_model import ToDo, ReminderType
from app.models.user_model import User
from app.schemas.todo_schema import ToDoCreate, ToDoUpdate


def calculate_remind_at(
        target_date: Optional[datetime.date],
        deadline_time: Optional[time],
        reminder_type: ReminderType,
) -> Optional[datetime]:
    if not target_date or reminder_type == ReminderType.NONE:
        return None

    if reminder_type in (ReminderType.DEADLINE, ReminderType.BOTH) and deadline_time:
        return datetime.combine(target_date, deadline_time)
    elif reminder_type == ReminderType.MORNING:
        return datetime.combine(target_date, time(9, 0))

    return None


async def create_todo(
        todo_data: ToDoCreate,
        user: User,
        db: AsyncSession
):
    remind_at = todo_data.remind_at or calculate_remind_at(
        todo_data.target_date, todo_data.deadline_time, todo_data.reminder_type
    )

    todo = ToDo(
        title=todo_data.title,
        description=todo_data.description,
        target_date=todo_data.target_date,
        deadline_time=todo_data.deadline_time,
        remind_at=remind_at,
        reminder_type=todo_data.reminder_type,
        user_id=user.id
    )

    db.add(todo)
    await db.commit()
    await db.refresh(todo)

    return todo


async def get_todos(
        user: User,
        db: AsyncSession,
        limit: int = 10,
        offset: int = 0,
        is_done: bool | None = None,
        sort_by: str = "created_at",
        order: str = "desc"
):
    sort_fields = {
        "id": ToDo.id,
        "title": ToDo.title,
        "is_done": ToDo.completed,
        "created_at": ToDo.created_at,
    }

    # 1. Валидация входных параметров
    if sort_by not in sort_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимое поле для сортировки. Разрешены: {list(sort_fields.keys())}"
        )

    if order not in ("asc", "desc"):
        raise HTTPException(
            status_code=400,
            detail="Параметр order должен быть 'asc' или 'desc'"
        )

    # 2. Базовый запрос
    query = select(ToDo).where(ToDo.user_id == user.id)

    # 3. Фильтрация по статусу выполнения
    if is_done is not None:
        query = query.where(ToDo.completed == is_done)

    # 4. Сортировка
    column = sort_fields[sort_by]
    sort_func = desc if order == "desc" else asc
    query = query.order_by(sort_func(column))

    # 5. Пагинация
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    return result.scalars().all()


async def get_todo_by_id(
        todo_id: int,
        user: User,
        db: AsyncSession
):
    result = await db.execute(
        select(ToDo).where(
            ToDo.id == todo_id,
            ToDo.user_id == user.id
        )
    )

    todo = result.scalar_one_or_none()

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    return todo


async def update_todo(
        todo_id: int,
        todo_data: ToDoUpdate,
        user: User,
        db: AsyncSession
):
    result = await db.execute(
        select(ToDo).where(
            ToDo.id == todo_id,
            ToDo.user_id == user.id
        )
    )

    todo = result.scalar_one_or_none()

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    data = todo_data.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(todo, key, value)

    # Пересчитываем remind_at, если изменились ключевые поля даты/времени
    if any(k in data for k in ("target_date", "deadline_time", "reminder_type")):
        todo.remind_at = calculate_remind_at(
            todo.target_date, todo.deadline_time, todo.reminder_type
        )

    await db.commit()
    await db.refresh(todo)

    return todo


async def delete_todo(
        todo_id: int,
        user: User,
        db: AsyncSession
):
    result = await db.execute(
        select(ToDo).where(
            ToDo.id == todo_id,
            ToDo.user_id == user.id
        )
    )

    todo = result.scalar_one_or_none()

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    await db.delete(todo)
    await db.commit()

    return {"message": "Todo deleted"}