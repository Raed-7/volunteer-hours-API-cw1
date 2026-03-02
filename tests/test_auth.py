def test_register_success(client):
    payload = {
        "email": "admin@example.com",
        "full_name": "Admin User",
        "password": "password123",
        "role": "admin",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201


def test_login_success(client):
    client.post(
        "/auth/register",
        json={
            "email": "organiser@example.com",
            "full_name": "Organiser User",
            "password": "password123",
            "role": "organiser",
        },
    )
    response = client.post("/auth/login", json={"email": "organiser@example.com", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_protected_route_requires_token(client):
    response = client.get("/volunteers")
    assert response.status_code == 403
