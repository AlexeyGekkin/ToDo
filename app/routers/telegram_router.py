from fastapi import Depends, APIRouter

from app.dependencies import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.telegram_auth_service import validate_init_data
from app.services.telegram_service import (
    get_profile,
    get_webapp_todos,
    create_webapp_todo, update_webapp_todo, delete_webapp_account,
)
from app.schemas.telegram_schema import (
    MiniAppToDoCreate,
    TaskStatusUpdate,
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
        db
    )

@router.get("/todos")
async def get_todos_for_webapp(
    init_data: str,
    db: AsyncSession = Depends(get_db),
):
    telegram_id = validate_init_data(init_data)

    return await get_webapp_todos(
        telegram_id,
        db,
    )

@router.post("/todos")
async def create_todo_webapp(
    data: MiniAppToDoCreate,
    db: AsyncSession = Depends(get_db),
):
    telegram_id = validate_init_data(
        data.init_data,
    )

    return await create_webapp_todo(
        telegram_id,
        data,
        db,
    )

@router.patch("/todos/{todo_id}")
async def update_todo_status(
    todo_id: int,
    status: TaskStatusUpdate,
    init_data: str,
    db: AsyncSession = Depends(get_db),
):
    telegram_id = validate_init_data(init_data)

    return await update_webapp_todo(
        telegram_id,
        todo_id,
        status.completed,
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