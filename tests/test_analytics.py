from datetime import datetime


def get_auth_header(client, email="analytics@example.com", role="organiser"):
    client.post(
        "/auth/register",
        json={
            "email": email,
            "full_name": "Analytics User",
            "password": "password123",
            "role": role,
        },
    )
    login_response = client.post("/auth/login", json={"email": email, "password": "password123"})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_volunteer(client, headers, name, email, phone="123456789"):
    response = client.post(
        "/volunteers",
        json={
            "full_name": name,
            "email": email,
            "phone": phone,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_event(client, headers, title, event_date="2026-01-15", location="Leeds"):
    response = client.post(
        "/events",
        json={
            "title": title,
            "description": f"{title} description",
            "location": location,
            "event_date": event_date,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_shift(client, headers, event_id, name, start_time, end_time):
    response = client.post(
        f"/events/{event_id}/shifts",
        json={
            "name": name,
            "description": f"{name} description",
            "start_time": start_time,
            "end_time": end_time,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_work_log(client, headers, volunteer_id, shift_id, checked_in_at, checked_out_at):
    response = client.post(
        "/work-logs",
        json={
            "volunteer_id": volunteer_id,
            "shift_id": shift_id,
            "checked_in_at": checked_in_at,
            "checked_out_at": checked_out_at,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_analytics_leaderboard_orders_by_total_hours(client):
    headers = get_auth_header(client, email="leaderboard@example.com")

    volunteer_1 = create_volunteer(client, headers, "Ahmed Ali", "ahmed@example.com")
    volunteer_2 = create_volunteer(client, headers, "Sara Khan", "sara@example.com")

    event = create_event(client, headers, "Leaderboard Event")

    shift_1 = create_shift(
        client,
        headers,
        event["id"],
        "Morning Shift",
        "2026-01-15T09:00:00",
        "2026-01-15T12:00:00",
    )
    shift_2 = create_shift(
        client,
        headers,
        event["id"],
        "Afternoon Shift",
        "2026-01-15T13:00:00",
        "2026-01-15T17:00:00",
    )

    create_work_log(
        client,
        headers,
        volunteer_1["id"],
        shift_1["id"],
        "2026-01-15T09:00:00",
        "2026-01-15T12:00:00",
    )  # 180 minutes

    create_work_log(
        client,
        headers,
        volunteer_2["id"],
        shift_2["id"],
        "2026-01-15T13:00:00",
        "2026-01-15T15:00:00",
    )  # 120 minutes

    response = client.get("/analytics/leaderboard", headers=headers)
    assert response.status_code == 200

    body = response.json()
    assert len(body) >= 2
    assert body[0]["name"] == "Ahmed Ali"
    assert body[0]["total_minutes"] == 180
    assert body[0]["total_hours"] == 3.0
    assert body[1]["name"] == "Sara Khan"
    assert body[1]["total_minutes"] == 120
    assert body[1]["total_hours"] == 2.0


def test_analytics_awards_groups_volunteers_into_tiers(client):
    headers = get_auth_header(client, email="awards@example.com")

    volunteer_a = create_volunteer(client, headers, "Tier A Volunteer", "tiera@example.com")
    volunteer_b = create_volunteer(client, headers, "Tier B Volunteer", "tierb@example.com")
    volunteer_c = create_volunteer(client, headers, "Tier C Volunteer", "tierc@example.com")

    event = create_event(client, headers, "Awards Event")

    shift_a = create_shift(
        client,
        headers,
        event["id"],
        "Tier A Shift",
        "2026-01-16T00:00:00",
        "2026-01-16T23:00:00",
    )
    shift_b = create_shift(
        client,
        headers,
        event["id"],
        "Tier B Shift",
        "2026-01-17T00:00:00",
        "2026-01-17T20:00:00",
    )
    shift_c = create_shift(
        client,
        headers,
        event["id"],
        "Tier C Shift",
        "2026-01-18T10:00:00",
        "2026-01-18T13:00:00",
    )

    create_work_log(
        client,
        headers,
        volunteer_a["id"],
        shift_a["id"],
        "2026-01-16T00:00:00",
        "2026-01-16T21:00:00",
    )  # 1260 minutes = 21 hours

    create_work_log(
        client,
        headers,
        volunteer_b["id"],
        shift_b["id"],
        "2026-01-17T00:00:00",
        "2026-01-17T16:00:00",
    )  # 960 minutes = 16 hours

    create_work_log(
        client,
        headers,
        volunteer_c["id"],
        shift_c["id"],
        "2026-01-18T10:00:00",
        "2026-01-18T12:00:00",
    )  # 120 minutes = 2 hours

    response = client.get("/analytics/awards", headers=headers)
    assert response.status_code == 200

    body = response.json()

    assert len(body["tier_a"]) == 1
    assert body["tier_a"][0]["name"] == "Tier A Volunteer"
    assert body["tier_a"][0]["total_hours"] == 21.0

    assert len(body["tier_b"]) == 1
    assert body["tier_b"][0]["name"] == "Tier B Volunteer"
    assert body["tier_b"][0]["total_hours"] == 16.0

    assert len(body["tier_c"]) == 1
    assert body["tier_c"][0]["name"] == "Tier C Volunteer"
    assert body["tier_c"][0]["total_hours"] == 2.0


def test_analytics_volunteer_summary_returns_totals_and_recent_activity(client):
    headers = get_auth_header(client, email="summary@example.com")

    volunteer = create_volunteer(client, headers, "Summary Volunteer", "summaryvol@example.com")

    event_1 = create_event(client, headers, "Summary Event One", event_date="2026-02-01")
    event_2 = create_event(client, headers, "Summary Event Two", event_date="2026-02-02")

    shift_1 = create_shift(
        client,
        headers,
        event_1["id"],
        "Setup Shift",
        "2026-02-01T09:00:00",
        "2026-02-01T11:00:00",
    )
    shift_2 = create_shift(
        client,
        headers,
        event_2["id"],
        "Welcome Shift",
        "2026-02-02T17:00:00",
        "2026-02-02T20:00:00",
    )

    create_work_log(
        client,
        headers,
        volunteer["id"],
        shift_1["id"],
        "2026-02-01T09:00:00",
        "2026-02-01T11:00:00",
    )  # 120 minutes

    create_work_log(
        client,
        headers,
        volunteer["id"],
        shift_2["id"],
        "2026-02-02T17:30:00",
        "2026-02-02T20:00:00",
    )  # 150 minutes

    response = client.get(f"/analytics/volunteers/{volunteer['id']}/summary", headers=headers)
    assert response.status_code == 200

    body = response.json()
    assert body["volunteer_id"] == volunteer["id"]
    assert body["name"] == "Summary Volunteer"
    assert body["total_events_worked"] == 2
    assert body["total_shifts_worked"] == 2
    assert body["total_minutes"] == 270
    assert body["total_hours"] == 4.5
    assert len(body["recent_activity"]) == 2
    assert body["recent_activity"][0]["event_title"] == "Summary Event Two"


def test_analytics_volunteer_summary_returns_404_for_missing_volunteer(client):
    headers = get_auth_header(client, email="missing-summary@example.com")

    response = client.get("/analytics/volunteers/999/summary", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Volunteer not found"