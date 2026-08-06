import pytest


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