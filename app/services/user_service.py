from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app import models, schemas
from app.models import User
from app.services.auth_service import  (
    hash_password,
    verify_password,
    create_access_token
)


async def register_user(
        user: schemas.UserCreate,
        db: AsyncSession
):
    result = await db.execute(
        select(models.User).where(
            models.User.email == user.email
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = models.User(
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)

    await db.commit()
    await db.refresh(new_user)

    return new_user


async def authenticate_user(
        user: schemas.UserCreate,
        db: AsyncSession
):
    result = await db.execute(
        select(models.User).where(
            models.User.email == user.email
        )
    )

    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        {
            "sub": str(db_user.id)
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

async def delete_user_account(user: User, db: AsyncSession) -> dict:

    await db.delete(user)
    await db.commit()
    return {"status": "ok", "message": "Аккаунт и все данные успешно удалены."}