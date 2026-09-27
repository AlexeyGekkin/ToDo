from datetime import date, datetime, time

from fastapi import HTTPException
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.todo_model import ReminderType, ToDo
from app.models.user_model import User
from app.schemas.todo_schema import ToDoCreate, ToDoUpdate


def calculate_remind_times(
    target_date: date | None,
    deadline_time: time | None,
    reminder_type: ReminderType,
) -> tuple[datetime | None, datetime | None]:

    morning_remind_at = None
    deadline_remind_at = None

    if not target_date or reminder_type == ReminderType.NONE:
        return morning_remind_at, deadline_remind_at

    if reminder_type in (ReminderType.MORNING, ReminderType.BOTH):
        morning_remind_at = datetime.combine(
            target_date,
            time(9, 0)
        )

    if reminder_type in (ReminderType.DEADLINE, ReminderType.BOTH):
        if deadline_time:
            deadline_remind_at = datetime.combine(
                target_date,
                deadline_time
            )

    return morning_remind_at, deadline_remind_at


async def get_user_todo(
    todo_id: int,
    user: User,
    db: AsyncSession,
) -> ToDo:
    result = await db.execute(
        select(ToDo).where(
            ToDo.id == todo_id,
            ToDo.user_id == user.id
        )
    )

    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=404,
            detail="Todo not found",
        )

    return todo


async def create_todo(
    todo_data: ToDoCreate,
    user: User,
    db: AsyncSession
):
    morning_remind_at, deadline_remind_at = calculate_remind_times(
        todo_data.target_date,
        todo_data.deadline_time,
        todo_data.reminder_type
    )

    todo = ToDo(
        title=todo_data.title,
        description=todo_data.description,
        target_date=todo_data.target_date,
        deadline_time=todo_data.deadline_time,
        morning_remind_at=morning_remind_at,
        deadline_remind_at=deadline_remind_at,
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
    if not 1 <= limit <= 100:
        raise HTTPException(
            status_code=400,
            detail="limit должен быть от 1 до 100"
        )

    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="offset не может быть отрицательным"
        )

    sort_fields = {
        "id": ToDo.id,
        "title": ToDo.title,
        "is_done": ToDo.completed,
        "created_at": ToDo.created_at,
    }

    if sort_by not in sort_fields:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Недопустимое поле для сортировки. "
                f"Разрешены: {list(sort_fields.keys())}"
            )
        )

    if order not in ("asc", "desc"):
        raise HTTPException(
            status_code=400,
            detail="Параметр order должен быть 'asc' или 'desc'"
        )

    query = select(ToDo).where(
        ToDo.user_id == user.id
    )

    if is_done is not None:
        query = query.where(
            ToDo.completed == is_done
        )

    column = sort_fields[sort_by]
    sort_func = desc if order == "desc" else asc

    query = query.order_by(
        sort_func(column)
    )

    query = query.limit(limit).offset(offset)

    result = await db.execute(query)

    return result.scalars().all()


async def update_todo(
    todo_id: int,
    todo_data: ToDoUpdate,
    user: User,
    db: AsyncSession
):
    todo = await get_user_todo(
        todo_id,
        user,
        db
    )

    data = todo_data.model_dump(
        exclude_unset=True
    )

    for key, value in data.items():
        setattr(todo, key, value)

    if any(
        key in data
        for key in (
            "target_date",
            "deadline_time",
            "reminder_type"
        )
    ):
        (
            todo.morning_remind_at,
            todo.deadline_remind_at
        ) = calculate_remind_times(
            todo.target_date,
            todo.deadline_time,
            todo.reminder_type
        )

    await db.commit()
    await db.refresh(todo)

    return todo


async def delete_todo(
    todo_id: int,
    user: User,
    db: AsyncSession
):
    todo = await get_user_todo(
        todo_id,
        user,
        db
    )

    await db.delete(todo)
    await db.commit()

    return {"message": "Todo deleted"}
