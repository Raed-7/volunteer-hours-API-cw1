def test_register_and_login(client):
    register_payload = {
        "email": "admin@example.com",
        "full_name": "Admin User",
        "password": "password123",
        "role": "admin",
    }
    register_response = client.post("/auth/register", json=register_payload)
    assert register_response.status_code == 201
    assert register_response.json()["email"] == register_payload["email"]

    login_response = client.post(
        "/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token

    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["role"] == "admin"


def test_protected_route_requires_token(client):
    response = client.get("/volunteers")
    assert response.status_code == 403
