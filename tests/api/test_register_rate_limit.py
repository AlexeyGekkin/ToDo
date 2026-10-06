import pytest


@pytest.mark.asyncio
async def test_register_rate_limit(client):
    for i in range(5):
        response = await client.post(
            "/users/register",
            json={
                "email": f"rate-register-{i}@example.com",
                "password": "12345678",
            },
        )

        assert response.status_code == 200

    response = await client.post(
        "/users/register",
        json={
            "email": "rate-register-6@example.com",
            "password": "12345678",
        },
    )

    assert response.status_code == 429