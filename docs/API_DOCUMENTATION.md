# API Documentation

## Overview

The **Volunteer Hours Management API** is a FastAPI backend for managing:

- users
- volunteers
- events
- shifts
- work logs
- CSV imports
- analytics
- project statistics

This API is designed for event organisers who need to track volunteer work accurately and generate useful summaries from stored data.

---

## Live Deployment

The API is deployed and publicly accessible at:

- **Homepage:** https://volunteer-hours-api-cw1.onrender.com/
- **API Docs:** https://volunteer-hours-api-cw1.onrender.com/docs
- **Admin Dashboard:** https://volunteer-hours-api-cw1.onrender.com/dashboard
- **Health Check:** https://volunteer-hours-api-cw1.onrender.com/health

> Note: The free tier may take up to 50 seconds to respond after a period of inactivity. Visit the homepage first to wake the server before testing.

## Local Base URL

`http://127.0.0.1:8000`

Interactive API docs: `/docs`

Homepage: `/`

Admin Dashboard: `/dashboard`

---

## Authentication

Most routes are protected and require a valid JWT access token.

### Auth flow

1. Register a user with `POST /auth/register`
2. Log in with `POST /auth/login`
3. Copy the returned `access_token`
4. In Swagger `/docs`, click **Authorize**
5. Paste: `Bearer YOUR_ACCESS_TOKEN`

### Roles

Supported roles:

- `admin`
- `organiser`

### Admin-only functionality

These routes are restricted to admin users:

- all import endpoints (`/imports/*`)
- volunteer deletion

---

## Route Groups

- `/` — homepage
- `/dashboard` — admin statistics dashboard
- `/auth` — authentication
- `/volunteers` — volunteer management
- `/events` — event management
- `/shifts` — shift management
- `/work-logs` — work log management
- `/imports` — CSV import (admin only)
- `/analytics` — leaderboard, awards, summaries
- `/stats` — system totals
- `/health` — health check

---

# Endpoints

## Home

### `GET /`

Returns the project homepage with links to key routes, feature cards, and an accessibility toolbar. The homepage includes:

- text size controls (small / medium / large)
- high-contrast greyscale colour-blind mode (WCAG 2.1 Level AAA)
- navigation links to `/docs`, `/dashboard`, and `/health`

---

## Admin Dashboard

### `GET /dashboard`

Returns an interactive HTML dashboard page. Paste a valid admin JWT token to load live system-wide statistics displayed as visual cards:

- total volunteers
- total events
- total shifts
- total work logs
- total worked minutes
- total worked hours

The token is sent via a client-side fetch request and is never stored.

---

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
  "volunteer_no": "V001",
  "name": "Ahmed Ali",
  "email": "ahmed@test.com",
  "phone": "772100000"
}
```

**Example response**

```json
{
  "id": 1,
  "volunteer_no": "V001",
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

- `effective_start = max(checked_in_at, shift.start_time)`
- `effective_end = min(checked_out_at, shift.end_time)`
- `worked_minutes = max(0, effective_end - effective_start)`

This prevents over-counting outside the planned shift window.

### Validation behaviour

Examples of rejected cases:

- `checked_out_at` before `checked_in_at`
- duplicate work log for the same volunteer and shift

---

## Imports

These routes are restricted to admin users.

### `POST /imports/volunteers`

Upload a CSV file of volunteers.

### `POST /imports/events`

Upload a CSV file of events.

### `POST /imports/attendance`

Upload a CSV file of attendance/work-log data.

### Flexible import behaviour

#### Volunteers import

Supports alternate column names including:

- `volunteer_no`, `volunteer_id`, `volunteer_number`
- `full_name`, `volunteer_name`
- `email`, `mail`
- `phone`, `mobile`

Can import volunteers when email or phone is missing, as long as a usable name exists.

#### Events import

Supports alternate column names including:

- `event_title`, `title`, `event_name`
- `event_date`, `date`
- `location`, `venue`
- `description`, `details`

Supports multiple date formats: `YYYY-MM-DD` and `DD/MM/YYYY`.

#### Attendance import

Accepts spreadsheet-style attendance data and converts it into stored work-log records.

### Example import response

```json
{
  "created": 10,
  "updated": 2,
  "skipped": 1
}
```

### Example CSV files

- `volunteers_import_template_en.csv`
- `events_import_template_en.csv`
- `attendance_import_template_en.csv`

Real datasets are also included under `datasets/` in the repository.

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

Return volunteers grouped by award tier based on total worked hours.

**Default award tiers**

- `tier_a`: 20 or more hours
- `tier_b`: 15 to less than 20 hours
- `tier_c`: 1 to less than 15 hours

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

Return a comprehensive summary for one volunteer.

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

## Stats

### `GET /stats`

Return overall system-wide totals. This endpoint requires authentication. Use the `/dashboard` page to view stats in a browser via JWT token.

**Example response**

```json
{
  "total_volunteers": 116,
  "total_events": 108,
  "total_shifts": 100,
  "total_work_logs": 383,
  "total_worked_minutes": 78120,
  "total_worked_hours": 1302.0
}
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| `200 OK` | Successful read or update |
| `201 Created` | Successful create |
| `204 No Content` | Successful delete |
| `400 Bad Request` | Invalid request or business-rule failure |
| `401 Unauthorized` | Missing or invalid token |
| `403 Forbidden` | Authenticated but not permitted |
| `404 Not Found` | Requested resource does not exist |
| `422 Unprocessable Entity` | Request validation error |

### Example validation error response

```json
{
  "detail": "Validation failed",
  "errors": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error"
    }
  ]
}
```

### Example resource error response

```json
{
  "detail": "Volunteer not found"
}
```

---

## Notes

- The base path `/` returns a homepage — not a 404
- The admin dashboard at `/dashboard` provides a visual stats view requiring a JWT token
- Auth registration uses `full_name`; volunteer payload uses `name` — this difference is intentional for compatibility
- Analytics are most meaningful after importing data or creating work logs manually
- Import endpoints are admin-protected