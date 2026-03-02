
def get_auth_header(client, email="org3@example.com", role="organiser"):
    client.post(
        "/auth/register",
        json={
            "email": email,
            "full_name": "User",
            "password": "password123",
            "role": role,
        },
    )
    login_response = client.post("/auth/login", json={"email": email, "password": "password123"})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_shift_worklog_and_hours_summary(client):
    headers = get_auth_header(client)

    volunteer = client.post(
        "/volunteers",
        json={"name": "Alice", "email": "alice@example.com"},
        headers=headers,
    ).json()

    event = client.post(
        "/events",
        json={
            "title": "Food Drive",
            "description": "Food collection",
            "location": "Hall",
            "event_date": "2026-02-01",
        },
        headers=headers,
    ).json()

    shift_resp = client.post(
        f"/events/{event['id']}/shifts",
        json={
            "name": "Morning Shift",
            "description": "Front desk",
            "start_time": "2026-02-01T09:00:00",
            "end_time": "2026-02-01T12:00:00",
        },
        headers=headers,
    )
    assert shift_resp.status_code == 201
    shift = shift_resp.json()

    work_log_resp = client.post(
        "/work-logs",
        json={
            "volunteer_id": volunteer["id"],
            "shift_id": shift["id"],
            "checked_in_at": "2026-02-01T08:30:00",
            "checked_out_at": "2026-02-01T12:30:00",
        },
        headers=headers,
    )
    assert work_log_resp.status_code == 201
    assert work_log_resp.json()["worked_minutes"] == 180

    volunteer_hours = client.get(f"/volunteers/{volunteer['id']}/hours", headers=headers)
    assert volunteer_hours.status_code == 200
    assert volunteer_hours.json()["worked_minutes"] == 180

    event_hours = client.get(f"/events/{event['id']}/hours", headers=headers)
    assert event_hours.status_code == 200
    assert event_hours.json()["worked_minutes"] == 180
