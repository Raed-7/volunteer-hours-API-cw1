def test_register_success(client):
    payload = {
def test_register_and_login(client):
    register_payload = {
        "email": "admin@example.com",
        "full_name": "Admin User",
        "password": "password123",
        "role": "admin",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    assert response.json()["email"] == payload["email"]


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

def test_protected_route_with_token(client):
    client.post(
        "/auth/register",
        json={
            "email": "member@example.com",
            "full_name": "Member User",
            "password": "password123",
            "role": "organiser",
        },
    )
    login = client.post("/auth/login", json={"email": "member@example.com", "password": "password123"})
    token = login.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_validation_error_message_shape(client):
    response = client.post("/auth/register", json={"email": "bad-email", "full_name": "A", "password": "123"})
    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "Validation failed"
    assert isinstance(body["errors"], list)
