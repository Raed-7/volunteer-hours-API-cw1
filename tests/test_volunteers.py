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


def test_volunteer_crud_happy_path(client):
    headers = get_auth_header(client)

    create_response = client.post(
        "/volunteers",
        json={"name": "John Volunteer", "email": "john@example.com", "phone": "123456789"},
        headers=headers,
    )
    assert create_response.status_code == 201
    volunteer = create_response.json()
    volunteer_id = volunteer["id"]

    list_response = client.get("/volunteers", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    detail_response = client.get(f"/volunteers/{volunteer_id}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["email"] == "john@example.com"

    update_response = client.patch(
        f"/volunteers/{volunteer_id}",
        json={"phone": "987654321"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["phone"] == "987654321"

    delete_response = client.delete(f"/volunteers/{volunteer_id}", headers=headers)
    assert delete_response.status_code == 204
