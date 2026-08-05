from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas import UserCreate
from app.models import User
from app.services.auth_service import  (
    hash_password,
    verify_password,
    create_access_token
)


async def get_user_by_email(
    email: str,
    db: AsyncSession,
) -> User | None:
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()

async def register_user(
        user: UserCreate,
        db: AsyncSession
):
    existing_user = await get_user_by_email(user.email, db)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = User(
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)

    await db.commit()
    await db.refresh(new_user)

    return new_user


async def authenticate_user(
        user: UserCreate,
        db: AsyncSession
):
    db_user = await get_user_by_email(user.email, db)

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