
def get_admin_auth_header(client):
    client.post(
        "/auth/register",
        json={
            "email": "admin2@example.com",
            "full_name": "Admin User",
            "password": "password123",
            "role": "admin",
        },
    )
    login_response = client.post("/auth/login", json={"email": "admin2@example.com", "password": "password123"})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_csv_import_basic_success(client):
    headers = get_admin_auth_header(client)

    volunteers_csv = "name,email,phone\nCsv User,csv@example.com,123\n"
    response = client.post(
        "/imports/volunteers",
        headers=headers,
        files={"file": ("volunteers.csv", volunteers_csv, "text/csv")},
    )
    assert response.status_code == 200
    assert response.json()["created"] == 1

    events_csv = "title,description,location,event_date\nCsv Event,Desc,Town Hall,2026-03-01\n"
    event_resp = client.post(
        "/imports/events",
        headers=headers,
        files={"file": ("events.csv", events_csv, "text/csv")},
    )
    assert event_resp.status_code == 200
    assert event_resp.json()["created"] == 1
