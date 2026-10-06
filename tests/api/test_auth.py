from datetime import UTC, date, datetime, time

import pytest

from app.models import ReminderType, ToDo
from app.schemas import UserCreate
from app.services.user_service import register_user, update_user_timezone


@pytest.mark.asyncio
async def test_register_success(client):
    payload = {
        "email": "test@example.com",
        "password": "12345678"
    }

    response = await client.post(
        "/users/register",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == payload["email"]
    assert data["id"] > 0

@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {
        "email": "test@example.com",
        "password": "12345678"
    }

    await client.post(
        "/users/register",
        json=payload,
    )

    response = await client.post(
        "/users/register",
        json=payload,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"

@pytest.mark.asyncio
async def test_login_success(client):
    payload = {
        "email": "test@example.com",
        "password": "12345678"
    }

    await client.post(
        "/users/register",
        json=payload,
    )

    response = await client.post(
        "/users/login",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_get_me_success(client,auth_token):

    response = await client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {auth_token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_get_me_without_token(client):

    response = await client.get(
        "/users/me"
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

@pytest.mark.asyncio
async def test_get_me_invalid_token(client):

    response = await client.get(
        "/users/me",
        headers={
            "Authorization": "Bearer Abra_ka_dabra"
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

@pytest.mark.asyncio
async def test_register_short_password(client):
    response = await client.post(
        "/users/register",
        json={
            "email": "short@example.com",
            "password": "1234567",
        },
    )

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_register_too_long_password(client):
    response = await client.post(
        "/users/register",
        json={
            "email": "long@example.com",
            "password": "a" * 129,
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    payload = {
        "email": "test@example.com",
        "password": "12345678"
    }

    await client.post(
        "/users/register",
        json=payload,
    )

    response = await client.post(
        "/users/login",
        json={
            "email": payload["email"],
            "password": "wrong_password"
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

@pytest.mark.asyncio
async def test_update_user_timezone(client, auth_token):
    response = await client.patch(
        "/users/me",
        json={"timezone": "Asia/Yekaterinburg"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    assert response.json()["timezone"] == "Asia/Yekaterinburg"

    response = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.json()["timezone"] == "Asia/Yekaterinburg"

@pytest.mark.asyncio
async def test_user_default_timezone(client, auth_token):
    response = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    assert response.json()["timezone"] == "Europe/Samara"

@pytest.mark.asyncio
async def test_timezone_update_recalculates_reminders(
    client,
    auth_token,
):
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    create_response = await client.post(
        "/todos/",
        json={
            "title": "Timezone test",
            "target_date": "2099-10-01",
            "deadline_time": "18:30:00",
            "reminder_type": "both",
        },
        headers=headers,
    )

    todo_id = create_response.json()["id"]

    assert (
        create_response.json()["morning_remind_at"]
        == "2099-10-01T04:00:00"
    )
    assert (
        create_response.json()["deadline_remind_at"]
        == "2099-10-01T14:30:00"
    )

    response = await client.patch(
        "/users/me",
        json={
            "timezone": "Asia/Yekaterinburg"
        },
        headers=headers,
    )

    assert response.status_code == 200

    todo_response = await client.get(
        f"/todos/{todo_id}",
        headers=headers,
    )

    data = todo_response.json()

    assert (
        data["morning_remind_at"]
        == "2099-10-01T03:00:00"
    )
    assert (
        data["deadline_remind_at"]
        == "2099-10-01T13:30:00"
    )

@pytest.mark.asyncio
async def test_timezone_update_does_not_restore_sent_reminder(
    db_session,
):
    user = await register_user(
        UserCreate(
            email="timezone@test.com",
            password="12345678",
        ),
        db_session,
    )

    todo = ToDo(
        title="Timezone reminder",
        target_date=date(2099, 10, 1),
        deadline_time=time(18, 30),
        reminder_type=ReminderType.BOTH,
        morning_remind_at=None,
        deadline_remind_at=datetime(
            2099,
            10,
            1,
            14,
            30,
            tzinfo=UTC,
        ),
        user_id=user.id,
    )

    db_session.add(todo)
    await db_session.commit()

    await update_user_timezone(
        user,
        "Asia/Yekaterinburg",
        db_session,
    )

    assert todo.morning_remind_at is None

    assert todo.deadline_remind_at is not None
    assert todo.deadline_remind_at.hour == 13
    assert todo.deadline_remind_at.minute == 30