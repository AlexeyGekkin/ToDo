from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import SessionLocal
from app import models, schemas
from app.auth import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


async def get_db():
    async with SessionLocal() as session:
        yield session


@router.post("/register")
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(models.User).where(models.User.email == user.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = models.User(
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {
        "id": new_user.id,
        "email": new_user.email
    }