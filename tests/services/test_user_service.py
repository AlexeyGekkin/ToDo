import pytest
from fastapi import HTTPException

from app.schemas.user_schema import UserCreate
from app.services.user_service import (
    register_user,
    get_user_by_email,
    authenticate_user,
    delete_user_account,
)


@pytest.mark.asyncio
async def test_register_user_service(db_session):

    user_data = UserCreate(
        email="service@test.com",
        password="12345678"
    )

    user = await register_user(
        user_data,
        db_session
    )

    assert user.id is not None
    assert user.email == user_data.email
    assert user.password != user_data.password


@pytest.mark.asyncio
async def test_register_user_duplicate_email(db_session):

    user_data = UserCreate(
        email="duplicate@test.com",
        password="12345678"
    )

    await register_user(
        user_data,
        db_session
    )

    with pytest.raises(HTTPException) as exc:

        await register_user(
            user_data,
            db_session
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Email already exists"


@pytest.mark.asyncio
async def test_get_user_by_email(db_session):

    user_data = UserCreate(
        email="find@test.com",
        password="12345678"
    )

    await register_user(
        user_data,
        db_session
    )

    user = await get_user_by_email(
        "find@test.com",
        db_session
    )

    assert user is not None
    assert user.email == "find@test.com"


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(db_session):

    user = await get_user_by_email(
        "none@test.com",
        db_session
    )

    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_success(db_session):

    user_data = UserCreate(
        email="auth@test.com",
        password="12345678"
    )

    await register_user(
        user_data,
        db_session
    )

    result = await authenticate_user(
        user_data,
        db_session
    )

    assert "access_token" in result
    assert result["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(db_session):

    await register_user(
        UserCreate(
            email="wrong@test.com",
            password="12345678"
        ),
        db_session
    )

    with pytest.raises(HTTPException) as exc:

        await authenticate_user(
            UserCreate(
                email="wrong@test.com",
                password="wrong_password"
            ),
            db_session
        )

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid credentials"


@pytest.mark.asyncio
async def test_delete_user_account(db_session):

    user = await register_user(
        UserCreate(
            email="delete@test.com",
            password="12345678"
        ),
        db_session
    )

    result = await delete_user_account(
        user,
        db_session
    )

    assert result["status"] == "ok"
    assert "успешно удалены" in result["message"]

    deleted_user = await get_user_by_email(
        "delete@test.com",
        db_session
    )

    assert deleted_user is None