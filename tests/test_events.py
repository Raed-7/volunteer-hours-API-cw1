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


def test_event_crud_happy_path(client):
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
    event_id = create_response.json()["id"]

    list_response = client.get("/events", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    detail_response = client.get(f"/events/{event_id}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["title"] == "Community Clean-up"

    update_response = client.patch(
        f"/events/{event_id}",
        json={"location": "Town Hall"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["location"] == "Town Hall"

    delete_response = client.delete(f"/events/{event_id}", headers=headers)
    assert delete_response.status_code == 204
