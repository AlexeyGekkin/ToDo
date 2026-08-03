from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.models.user_model import User
from app.schemas import todo_schema
from app.services.todo_service import (create_todo,
                                       get_todos,
                                       get_todo_by_id,
                                       update_todo,
                                       delete_todo)


router = APIRouter(
    prefix="/todos",
    tags=["Todos"]
)


@router.post(
    "/",
    response_model=todo_schema.ToDoResponse
)
async def add_todo(
        todo: todo_schema.ToDoCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await create_todo(
        todo,
        current_user,
        db
    )

@router.get(
    "/",
    response_model=list[todo_schema.ToDoResponse]
)
async def get_all_todos(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        is_done: bool | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await get_todos(
        current_user,
        db,
        limit,
        offset,
        is_done,
        sort_by,
        order
    )

@router.get(
    "/{todo_id}",
    response_model=todo_schema.ToDoResponse
)
async def get_todo(
        todo_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await get_todo_by_id(
        todo_id,
        current_user,
        db
    )

@router.patch(
    "/{todo_id}",
    response_model=todo_schema.ToDoResponse
)
async def patch_todo(
        todo_id: int,
        todo: todo_schema.ToDoUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await update_todo(
        todo_id,
        todo,
        current_user,
        db
    )

@router.delete("/{todo_id}")
async def remove_todo(
        todo_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await delete_todo(
        todo_id,
        current_user,
        db
    )