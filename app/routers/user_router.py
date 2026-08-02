from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas

from app.dependencies import get_current_user, get_db
from app.models import User
from app.services.user_service import (
    register_user,
    authenticate_user
)


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me", response_model=schemas.UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post(
    "/register",
    response_model=schemas.UserResponse
)
async def register(
        user: schemas.UserCreate,
        db: AsyncSession = Depends(get_db)
):
    return await register_user(user, db)


@router.post("/login", response_model=schemas.TokenResponse)
async def login(
        user: schemas.UserCreate,
        db: AsyncSession = Depends(get_db)
):
    return await authenticate_user(user, db)