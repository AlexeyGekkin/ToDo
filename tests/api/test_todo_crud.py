import pytest


@pytest.mark.asyncio
async def test_create_todo(client, auth_token):
    payload = {
        "title": "Test todo",
        "description": "Description"
    }

    response = await client.post(
        "/todos/",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["completed"] is False
    assert data["morning_remind_at"] is None
    assert data["deadline_remind_at"] is None


@pytest.mark.asyncio
async def test_get_todos(client, auth_token):
    await client.post(
        "/todos/",
        json={
            "title": "Todo 1",
            "description": "First"
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    response = await client.get(
        "/todos/",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Todo 1"


@pytest.mark.asyncio
async def test_get_single_todo(client, auth_token):
    create_response = await client.post(
        "/todos/",
        json={"title": "Single todo"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    todo_id = create_response.json()["id"]

    response = await client.get(
        f"/todos/{todo_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == todo_id
    assert data["title"] == "Single todo"


@pytest.mark.asyncio
async def test_update_todo(client, auth_token):
    create_response = await client.post(
        "/todos/",
        json={"title": "Old title"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    todo_id = create_response.json()["id"]

    response = await client.patch(
        f"/todos/{todo_id}",
        json={
            "title": "New title",
            "completed": True
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "New title"
    assert data["completed"] is True


@pytest.mark.asyncio
async def test_delete_todo(client, auth_token):
    create_response = await client.post(
        "/todos/",
        json={"title": "Delete me"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    todo_id = create_response.json()["id"]

    response = await client.delete(
        f"/todos/{todo_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Todo deleted"