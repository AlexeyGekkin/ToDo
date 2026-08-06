def test_register_success(client):
    payload = {
        "email": "test@example.com",
        "password": "12345678",
    }

    response = client.post("/users/register", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["email"] == payload["email"]
    assert isinstance(data["id"], int)
    assert "password" not in data