from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from  sqlalchemy import select

from app.models.todo_model import ToDo
from app.models.user_model import User
from app.schemas.todo_schema import TodoCreate, TodoUpdate


async def create_todo(
        todo_data: TodoCreate,
        user: User,
        db: AsyncSession
):
    todo = ToDo(
        title=todo_data.title,
        description=todo_data.description,
        user_id=user.id
    )

    db.add(todo)

    await db.commit()
    await db.refresh(todo)

    return todo

async def get_todos(
        user,
        db
):
    result = await db.execute(
        select(ToDo).where(
            ToDo.user_id == user.id
        )
    )

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
        todo_data: TodoUpdate,
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

    return {
        "message": "Todo deleted"
    }