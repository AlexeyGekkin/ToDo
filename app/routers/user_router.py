from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app import schemas
from app.dependencies import get_current_user, get_db
from app.models import User
from app.services.rate_limit_service import (
    login_rate_limiter,
    register_rate_limiter
)
from app.services.user_service import (
    authenticate_user,
    create_telegram_link,
    delete_user_account,
    register_user,
    update_user_timezone,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/telegram/link-url")
async def get_telegram_link(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    token = await create_telegram_link(current_user, db)

    link = (
        f"https://t.me/Gekkin_Alexey_notification_bot"
        f"?start={token}"
    )

    return {"link": link}

@router.get("/me", response_model=schemas.UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=schemas.UserResponse)
async def update_me(
    user_data: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await update_user_timezone(
        current_user,
        user_data.timezone,
        db,
    )

@router.post(
    "/register",
    response_model=schemas.UserResponse
)
async def register(
    user: schemas.UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    client_ip = request.client.host

    register_rate_limiter.check(client_ip)
    register_rate_limiter.add_attempt(client_ip)

    return await register_user(user, db)


@router.post(
    "/login",
    response_model=schemas.TokenResponse,
)
async def login(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    key = str(user.email).lower()

    login_rate_limiter.check(key)

    try:
        result = await authenticate_user(
            user,
            db,
        )
    except HTTPException as exc:
        if exc.status_code == 401:
            login_rate_limiter.add_attempt(key)

        raise

    login_rate_limiter.reset(key)

    return result

class DeleteAccountConfirm(BaseModel):
    confirmation: str = Field(
        ...,
        description="Для подтверждения необходимо ввести 'DELETE'",
        examples=["DELETE"],
    )


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_me(
    payload: DeleteAccountConfirm,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.confirmation != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверное слово подтверждения. Введите 'DELETE'.",
        )

    return await delete_user_account(current_user, db)