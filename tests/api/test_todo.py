import pytest


@pytest.mark.asyncio
async def test_get_todos_without_token(client):
    response = await client.get("/todos/")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_filter_completed_todos(client, auth_token):
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    done_response = await client.post(
        "/todos/",
        json={"title": "Done todo"},
        headers=headers,
    )

    done_id = done_response.json()["id"]

    await client.patch(
        f"/todos/{done_id}",
        json={"completed": True},
        headers=headers,
    )

    await client.post(
        "/todos/",
        json={"title": "Active todo"},
        headers=headers,
    )

    response = await client.get(
        "/todos/?is_done=false",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Active todo"
    assert data[0]["completed"] is False


@pytest.mark.asyncio
async def test_sort_todos_by_title(client, auth_token):
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    await client.post(
        "/todos/",
        json={"title": "ZZZ"},
        headers=headers,
    )

    await client.post(
        "/todos/",
        json={"title": "AAA"},
        headers=headers,
    )

    response = await client.get(
        "/todos/?sort_by=title&order=asc",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data[0]["title"] == "AAA"
    assert data[1]["title"] == "ZZZ"


@pytest.mark.asyncio
async def test_todos_pagination(client, auth_token):
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    await client.post(
        "/todos/",
        json={"title": "Todo 1"},
        headers=headers,
    )

    await client.post(
        "/todos/",
        json={"title": "Todo 2"},
        headers=headers,
    )

    response = await client.get(
        "/todos/?limit=1&offset=0",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1



@pytest.mark.asyncio
async def test_user_cannot_get_other_user_todo(
    client,
    auth_token,
    second_auth_token
):
    response = await client.post(
        "/todos/",
        json={"title": "Private todo"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    todo_id = response.json()["id"]

    response = await client.get(
        f"/todos/{todo_id}",
        headers={"Authorization": f"Bearer {second_auth_token}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_user_cannot_update_other_user_todo(
    client,
    auth_token,
    second_auth_token
):
    response = await client.post(
        "/todos/",
        json={"title": "Private todo"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    todo_id = response.json()["id"]

    response = await client.patch(
        f"/todos/{todo_id}",
        json={"title": "Hacked title"},
        headers={"Authorization": f"Bearer {second_auth_token}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_user_cannot_delete_other_user_todo(
    client,
    auth_token,
    second_auth_token
):
    response = await client.post(
        "/todos/",
        json={"title": "Private todo"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    todo_id = response.json()["id"]

    response = await client.delete(
        f"/todos/{todo_id}",
        headers={"Authorization": f"Bearer {second_auth_token}"},
    )

    assert response.status_code == 404

