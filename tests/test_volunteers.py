def get_auth_header(client):
    client.post(
        "/auth/register",
        json={
            "email": "org@example.com",
            "full_name": "Org User",
            "password": "password123",
            "role": "organiser",
        },
    )
    login_response = client.post("/auth/login", json={"email": "org@example.com", "password": "password123"})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_volunteer_create_list_happy_path(client):
    headers = get_auth_header(client)

    create_response = client.post(
        "/volunteers",
        json={"full_name": "John Volunteer", "email": "john@example.com", "phone": "123456789"},
        headers=headers,
    )
    assert create_response.status_code == 201

    list_response = client.get("/volunteers", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
