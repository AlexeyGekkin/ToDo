import pytest
from datetime import date, time, datetime

from fastapi import HTTPException

from app.models.todo_model import ReminderType
from app.schemas.todo_schema import ToDoCreate, ToDoUpdate
from app.services.todo_service import (
    create_todo,
    get_user_todo,
    update_todo,
    delete_todo,
    get_todos,
    calculate_remind_at,
)
from app.services.user_service import register_user
from app.schemas.user_schema import UserCreate

def test_calculate_remind_at_deadline():

    result = calculate_remind_at(
        date(2026, 8, 10),
        time(18, 30),
        ReminderType.DEADLINE,
    )

    assert result == datetime(
        2026, 8, 10, 18, 30
    )


def test_calculate_remind_at_morning():

    result = calculate_remind_at(
        date(2026, 8, 10),
        None,
        ReminderType.MORNING,
    )

    assert result == datetime(
        2026, 8, 10, 9, 0
    )


def test_calculate_remind_at_none():

    result = calculate_remind_at(
        None,
        None,
        ReminderType.DEADLINE,
    )

    assert result is None

@pytest.mark.asyncio
async def test_create_todo_service(db_session):

    user = await register_user(
        UserCreate(
            email="todo@test.com",
            password="12345678"
        ),
        db_session
    )

    todo_data = ToDoCreate(
        title="Test todo",
        description="Description"
    )

    todo = await create_todo(
        todo_data,
        user,
        db_session
    )

    assert todo.id is not None
    assert todo.title == "Test todo"
    assert todo.user_id == user.id


@pytest.mark.asyncio
async def test_get_user_todo_service(db_session):

    user = await register_user(
        UserCreate(
            email="get@test.com",
            password="12345678"
        ),
        db_session
    )

    todo = await create_todo(
        ToDoCreate(
            title="Find todo"
        ),
        user,
        db_session
    )

    result = await get_user_todo(
        todo.id,
        user,
        db_session
    )

    assert result.id == todo.id
    assert result.title == "Find todo"


@pytest.mark.asyncio
async def test_get_user_todo_not_found(db_session):

    user = await register_user(
        UserCreate(
            email="none@test.com",
            password="12345678"
        ),
        db_session
    )

    with pytest.raises(HTTPException) as exc:

        await get_user_todo(
            999,
            user,
            db_session
        )

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_todo_service(db_session):

    user = await register_user(
        UserCreate(
            email="update@test.com",
            password="12345678"
        ),
        db_session
    )

    todo = await create_todo(
        ToDoCreate(
            title="Old title"
        ),
        user,
        db_session
    )

    updated = await update_todo(
        todo.id,
        ToDoUpdate(
            title="New title",
            completed=True
        ),
        user,
        db_session
    )

    assert updated.title == "New title"
    assert updated.completed is True


@pytest.mark.asyncio
async def test_delete_todo_service(db_session):

    user = await register_user(
        UserCreate(
            email="delete@test.com",
            password="12345678"
        ),
        db_session
    )

    todo = await create_todo(
        ToDoCreate(
            title="Delete"
        ),
        user,
        db_session
    )

    result = await delete_todo(
        todo.id,
        user,
        db_session
    )

    assert result["message"] == "Todo deleted"

    with pytest.raises(HTTPException):
        await get_user_todo(
            todo.id,
            user,
            db_session
        )


@pytest.mark.asyncio
async def test_get_todos_service(db_session):

    user = await register_user(
        UserCreate(
            email="list@test.com",
            password="12345678"
        ),
        db_session
    )

    await create_todo(
        ToDoCreate(title="Todo 1"),
        user,
        db_session
    )

    await create_todo(
        ToDoCreate(title="Todo 2"),
        user,
        db_session
    )

    todos = await get_todos(
        user,
        db_session
    )

    assert len(todos) == 2


def test_calculate_remind_at_deadline():

    result = calculate_remind_at(
        date(2026, 8, 10),
        time(18, 30),
        ReminderType.DEADLINE
    )

    assert result == datetime(
        2026,
        8,
        10,
        18,
        30
    )


def test_calculate_remind_at_morning():

    result = calculate_remind_at(
        date(2026, 8, 10),
        None,
        ReminderType.MORNING
    )

    assert result == datetime(
        2026,
        8,
        10,
        9,
        0
    )