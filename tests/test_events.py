def get_auth_header(client):
    client.post(
        "/auth/register",
        json={
            "email": "org2@example.com",
            "full_name": "Org User 2",
            "password": "password123",
            "role": "organiser",
        },
    )
    login_response = client.post("/auth/login", json={"email": "org2@example.com", "password": "password123"})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_event_create_list_happy_path(client):
    headers = get_auth_header(client)

    create_response = client.post(
        "/events",
        json={
            "title": "Community Clean-up",
            "description": "Neighborhood volunteering event",
            "location": "City Park",
            "event_date": "2026-01-15",
        },
        headers=headers,
    )
    assert create_response.status_code == 201

    list_response = client.get("/events", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
