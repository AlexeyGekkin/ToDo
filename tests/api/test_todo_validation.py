import pytest


@pytest.mark.asyncio
async def test_create_todo_empty_title(client, auth_token):
    response = await client.post(
        "/todos/",
        json={"title": "     "},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_todo_title_is_stripped(client, auth_token):
    response = await client.post(
        "/todos/",
        json={"title": "   Buy milk   "},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Buy milk"

@pytest.mark.asyncio
async def test_update_todo_title_null(client, auth_token):
    create_response = await client.post(
        "/todos/",
        json={"title": "Old title"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    todo_id = create_response.json()["id"]

    response = await client.patch(
        f"/todos/{todo_id}",
        json={"title": None},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_update_todo_title_is_stripped(client, auth_token):
    create_response = await client.post(
        "/todos/",
        json={"title": "Old title"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    todo_id = create_response.json()["id"]

    response = await client.patch(
        f"/todos/{todo_id}",
        json={"title": "   New title   "},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "New title"