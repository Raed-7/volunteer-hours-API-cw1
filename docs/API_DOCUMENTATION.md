# API Documentation

## Overview

The **Volunteer Hours Management API** is a FastAPI backend for managing:

* users
* volunteers
* events
* shifts
* work logs
* CSV imports
* analytics

This API is designed for event organisers who need to track volunteer work accurately and generate useful summaries from stored data.

## Base URL

Local development base URL:

`http://127.0.0.1:8000`

Interactive API docs:

* `/docs`
* `/redoc`

---

## Authentication

Most routes are protected and require a valid JWT access token.

### Auth flow

1. Register a user with `POST /auth/register`
2. Log in with `POST /auth/login`
3. Copy the returned `access_token`
4. In Swagger `/docs`, click **Authorize**
5. Paste:

`Bearer YOUR_ACCESS_TOKEN`

### Roles

Supported roles:

* `admin`
* `organiser`

### Admin-only functionality

These routes should only be used by an admin:

* import endpoints
* destructive routes if admin restriction is applied there

---

## Route Groups

* `/auth`
* `/volunteers`
* `/events`
* `/shifts`
* `/work-logs`
* `/imports`
* `/analytics`
* `/health`

---

# Endpoints

## Health

### `GET /health`

Simple health check endpoint.

**Response**

```json
{
  "status": "ok"
}
```

---

## Authentication

### `POST /auth/register`

Register a new user.

**Example request**

```json
{
  "email": "admin@test.com",
  "full_name": "Admin User",
  "password": "Test12345!",
  "role": "admin"
}
```

**Example response**

```json
{
  "id": 1,
  "email": "admin@test.com",
  "full_name": "Admin User",
  "role": "admin"
}
```

### `POST /auth/login`

Authenticate a user and return a JWT access token.

**Example request**

```json
{
  "email": "admin@test.com",
  "password": "Test12345!"
}
```

**Example response**

```json
{
  "access_token": "your.jwt.token",
  "token_type": "bearer"
}
```

### `GET /auth/me`

Return the currently authenticated user.

**Response**

```json
{
  "id": 1,
  "email": "admin@test.com",
  "full_name": "Admin User",
  "role": "admin"
}
```

---

## Volunteers

### `POST /volunteers`

Create a volunteer.

**Example request**

```json
{
  "name": "Ahmed Ali",
  "email": "ahmed@test.com",
  "phone": "772100000"
}
```

**Example response**

```json
{
  "id": 1,
  "name": "Ahmed Ali",
  "email": "ahmed@test.com",
  "phone": "772100000"
}
```

### `GET /volunteers`

List all volunteers.

### `GET /volunteers/{volunteer_id}`

Get one volunteer by ID.

### `PATCH /volunteers/{volunteer_id}`

Update a volunteer.

**Example request**

```json
{
  "phone": "770000001"
}
```

### `DELETE /volunteers/{volunteer_id}`

Delete a volunteer.

### `GET /volunteers/{volunteer_id}/hours`

Return total worked time for one volunteer.

**Example response**

```json
{
  "target_id": 1,
  "worked_minutes": 150,
  "worked_hours": 2.5
}
```

---

## Events

### `POST /events`

Create an event.

**Example request**

```json
{
  "title": "Saudi National Day",
  "description": "Main event",
  "location": "Leeds",
  "event_date": "2025-09-27"
}
```

**Example response**

```json
{
  "id": 1,
  "title": "Saudi National Day",
  "description": "Main event",
  "location": "Leeds",
  "event_date": "2025-09-27"
}
```

### `GET /events`

List all events.

### `GET /events/{event_id}`

Get one event by ID.

### `PATCH /events/{event_id}`

Update an event.

### `DELETE /events/{event_id}`

Delete an event.

### `GET /events/{event_id}/hours`

Return total volunteer time recorded for one event.

**Example response**

```json
{
  "target_id": 1,
  "worked_minutes": 480,
  "worked_hours": 8.0
}
```

---

## Shifts

### `POST /events/{event_id}/shifts`

Create a shift for an event.

**Example request**

```json
{
  "name": "Morning Shift",
  "description": "Setup and preparation",
  "start_time": "2025-09-27T09:00:00",
  "end_time": "2025-09-27T12:00:00"
}
```

### `GET /events/{event_id}/shifts`

List all shifts for an event.

### `GET /shifts/{shift_id}`

Get one shift by ID.

### `PATCH /shifts/{shift_id}`

Update a shift.

### `DELETE /shifts/{shift_id}`

Delete a shift.

---

## Work Logs

### `POST /work-logs`

Create a work log.

**Example request**

```json
{
  "volunteer_id": 1,
  "shift_id": 1,
  "checked_in_at": "2025-09-27T09:15:00",
  "checked_out_at": "2025-09-27T11:45:00"
}
```

**Example response**

```json
{
  "id": 1,
  "volunteer_id": 1,
  "shift_id": 1,
  "checked_in_at": "2025-09-27T09:15:00",
  "checked_out_at": "2025-09-27T11:45:00",
  "worked_minutes": 150
}
```

### `GET /work-logs/{work_log_id}`

Get one work log by ID.

### `PATCH /work-logs/{work_log_id}`

Update a work log.

### `DELETE /work-logs/{work_log_id}`

Delete a work log.

### Worked-hours calculation

Worked time is calculated automatically using shift boundaries:

* `effective_start = max(checked_in_at, shift.start_time)`
* `effective_end = min(checked_out_at, shift.end_time)`
* `worked_minutes = max(0, effective_end - effective_start)`

This prevents over-counting outside the planned shift window.

### Validation behavior

Examples of rejected cases:

* `checked_out_at` before `checked_in_at`
* duplicate work log for the same volunteer and shift

---

## Imports

These routes are intended for admin users.

### `POST /imports/volunteers`

Upload a CSV file of volunteers.

### `POST /imports/events`

Upload a CSV file of events.

### `POST /imports/attendance`

Upload a CSV file of attendance/work-log data.

### Expected CSV files

* `volunteers_import_template_en.csv`
* `events_import_template_en.csv`
* `attendance_import_template_en.csv`

### Example import response

```json
{
  "created": 10,
  "updated": 2
}
```

---

## Analytics

### `GET /analytics/leaderboard`

Return volunteers ranked by total worked hours.

**Example response**

```json
[
  {
    "volunteer_id": 1,
    "name": "Ahmed Ali",
    "total_minutes": 600,
    "total_hours": 10.0
  }
]
```

### `GET /analytics/awards`

Return volunteers grouped by award tier.

### Default award tiers

* `tier_a`: 20 or more hours
* `tier_b`: 15 to less than 20 hours
* `tier_c`: 1 to less than 15 hours

**Example response**

```json
{
  "tier_a": [],
  "tier_b": [],
  "tier_c": [
    {
      "volunteer_id": 1,
      "name": "Ahmed Ali",
      "total_minutes": 600,
      "total_hours": 10.0
    }
  ]
}
```

### `GET /analytics/volunteers/{volunteer_id}/summary`

Return a volunteer summary.

**Example response**

```json
{
  "volunteer_id": 1,
  "name": "Ahmed Ali",
  "total_events_worked": 2,
  "total_shifts_worked": 3,
  "total_minutes": 600,
  "total_hours": 10.0,
  "recent_activity": [
    {
      "event_id": 1,
      "event_title": "Saudi National Day",
      "shift_id": 2,
      "shift_name": "Evening Shift",
      "checked_in_at": "2025-09-27T17:00:00",
      "checked_out_at": "2025-09-27T19:00:00",
      "worked_minutes": 120,
      "worked_hours": 2.0
    }
  ]
}
```

---

## Error Codes

Common error responses:

* `200 OK` — successful read/update
* `201 Created` — successful create
* `204 No Content` — successful delete
* `400 Bad Request` — invalid request or business-rule failure
* `401 Unauthorized` — missing or invalid token
* `403 Forbidden` — authenticated but not allowed
* `404 Not Found` — requested resource does not exist
* `422 Unprocessable Entity` — request validation error

### Example error response

```json
{
  "detail": "Volunteer not found"
}
```

---

## Notes

* The base path `/` may return `404 Not Found`; use `/docs` for the main interactive interface
* Auth registration currently uses `full_name`
* Volunteer payload currently uses `name`
* Analytics are most meaningful after importing data or creating work logs manually
