import pytest


@pytest.mark.asyncio
async def test_create_todo_morning_reminder(client, auth_token):
    response = await client.post(
        "/todos/",
        json={
            "title": "Morning reminder",
            "target_date": "2099-10-01",
            "reminder_type": "morning"
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["reminder_type"] == "morning"
    assert data["morning_remind_at"] == "2099-10-01T04:00:00"
    assert data["deadline_remind_at"] is None


@pytest.mark.asyncio
async def test_create_todo_deadline_reminder(client, auth_token):
    response = await client.post(
        "/todos/",
        json={
            "title": "Deadline reminder",
            "target_date": "2099-10-01",
            "deadline_time": "18:30:00",
            "reminder_type": "deadline"
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["reminder_type"] == "deadline"
    assert data["morning_remind_at"] is None
    assert data["deadline_remind_at"] == "2099-10-01T14:30:00"


@pytest.mark.asyncio
async def test_create_todo_both_reminders(client, auth_token):
    response = await client.post(
        "/todos/",
        json={
            "title": "Both reminders",
            "target_date": "2099-10-01",
            "deadline_time": "18:30:00",
            "reminder_type": "both"
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["reminder_type"] == "both"
    assert data["morning_remind_at"] == "2099-10-01T04:00:00"
    assert data["deadline_remind_at"] == "2099-10-01T14:30:00"


@pytest.mark.asyncio
async def test_create_deadline_reminder_without_time(
    client,
    auth_token,
):
    response = await client.post(
        "/todos/",
        json={
            "title": "No deadline time",
            "target_date": "2099-10-01",
            "reminder_type": "deadline",
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Deadline time is required for deadline reminders"
    )

@pytest.mark.asyncio
async def test_create_reminder_without_target_date(
    client,
    auth_token,
):
    response = await client.post(
        "/todos/",
        json={
            "title": "No target date",
            "reminder_type": "morning",
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Target date is required for reminders"
    )

@pytest.mark.asyncio
async def test_update_cannot_remove_deadline_time(
    client,
    auth_token,
):
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    create_response = await client.post(
        "/todos/",
        json={
            "title": "Deadline task",
            "target_date": "2099-10-01",
            "deadline_time": "18:30:00",
            "reminder_type": "deadline",
        },
        headers=headers,
    )

    todo_id = create_response.json()["id"]

    response = await client.patch(
        f"/todos/{todo_id}",
        json={
            "deadline_time": None,
        },
        headers=headers,
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Deadline time is required for deadline reminders"
    )

@pytest.mark.asyncio
async def test_update_todo_reminder_type(client, auth_token):
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    create_response = await client.post(
        "/todos/",
        json={
            "title": "Update reminder",
            "target_date": "2099-10-01",
            "deadline_time": "18:30:00"
        },
        headers=headers,
    )

    todo_id = create_response.json()["id"]

    response = await client.patch(
        f"/todos/{todo_id}",
        json={
            "reminder_type": "both"
        },
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["reminder_type"] == "both"
    assert data["morning_remind_at"] == "2099-10-01T04:00:00"
    assert data["deadline_remind_at"] == "2099-10-01T14:30:00"


@pytest.mark.asyncio
async def test_update_todo_deadline_time(client, auth_token):
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    create_response = await client.post(
        "/todos/",
        json={
            "title": "Update deadline",
            "target_date": "2099-10-01",
            "deadline_time": "18:30:00",
            "reminder_type": "deadline"
        },
        headers=headers,
    )

    todo_id = create_response.json()["id"]

    response = await client.patch(
        f"/todos/{todo_id}",
        json={
            "deadline_time": "20:00:00"
        },
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["deadline_time"] == "20:00:00"
    assert data["deadline_remind_at"] == "2099-10-01T16:00:00"