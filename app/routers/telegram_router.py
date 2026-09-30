from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.todo_schema import (
    ToDoCreate,
    ToDoUpdate,
)
from app.services.telegram_auth_service import validate_init_data
from app.services.telegram_service import (
    delete_webapp_account,
    get_profile,
    get_user_by_telegram_id,
)
from app.services.todo_service import (
    create_todo,
    get_todos,
    update_todo,
)

router = APIRouter(
    prefix="/api/telegram",
    tags=["Telegram"]
)


@router.get("/profile")
async def get_profile_webapp(
    init_data: str,
    db: AsyncSession = Depends(get_db),
):
    telegram_id = validate_init_data(init_data)

    return await get_profile(
        telegram_id,
        db,
    )


@router.get("/todos")
async def get_todos_for_webapp(
    init_data: str,
    db: AsyncSession = Depends(get_db),
):
    telegram_id = validate_init_data(init_data)

    user = await get_user_by_telegram_id(
        telegram_id,
        db,
    )

    return await get_todos(
        user,
        db,
    )


@router.post("/todos")
async def create_todo_webapp(
    todo: ToDoCreate,
    init_data: str,
    db: AsyncSession = Depends(get_db),
):
    telegram_id = validate_init_data(init_data)

    user = await get_user_by_telegram_id(
        telegram_id,
        db,
    )

    return await create_todo(
        todo,
        user,
        db,
    )


@router.patch("/todos/{todo_id}")
async def update_todo_webapp(
    todo_id: int,
    todo: ToDoUpdate,
    init_data: str,
    db: AsyncSession = Depends(get_db),
):
    telegram_id = validate_init_data(init_data)

    user = await get_user_by_telegram_id(
        telegram_id,
        db,
    )

    return await update_todo(
        todo_id,
        todo,
        user,
        db,
    )


@router.delete("/account")
async def delete_account_webapp(
    init_data: str,
    db: AsyncSession = Depends(get_db),
):
    telegram_id = validate_init_data(init_data)

    return await delete_webapp_account(
        telegram_id,
        db,
    )