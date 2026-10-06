import pytest


@pytest.mark.asyncio
async def test_login_rate_limit(client):
    payload = {
        "email": "rate-login@example.com",
        "password": "12345678",
    }

    response = await client.post(
        "/users/register",
        json=payload,
    )

    assert response.status_code == 200

    for _ in range(5):
        response = await client.post(
            "/users/login",
            json={
                "email": payload["email"],
                "password": "wrong_password",
            },
        )

        assert response.status_code == 401

    response = await client.post(
        "/users/login",
        json={
            "email": payload["email"],
            "password": "wrong_password",
        },
    )

    assert response.status_code == 429
    assert response.json()["detail"] == (
        "Too many login attempts"
    )


@pytest.mark.asyncio
async def test_successful_login_resets_rate_limit(client):
    payload = {
        "email": "rate-reset@example.com",
        "password": "12345678",
    }

    response = await client.post(
        "/users/register",
        json=payload,
    )

    assert response.status_code == 200

    for _ in range(4):
        response = await client.post(
            "/users/login",
            json={
                "email": payload["email"],
                "password": "wrong_password",
            },
        )

        assert response.status_code == 401

    response = await client.post(
        "/users/login",
        json=payload,
    )

    assert response.status_code == 200

    for _ in range(5):
        response = await client.post(
            "/users/login",
            json={
                "email": payload["email"],
                "password": "wrong_password",
            },
        )

        assert response.status_code == 401

    response = await client.post(
        "/users/login",
        json={
            "email": payload["email"],
            "password": "wrong_password",
        },
    )

    assert response.status_code == 429