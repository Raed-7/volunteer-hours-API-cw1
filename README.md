# Volunteer Hours Management API

Backend API for managing volunteers, events, shifts, and attendance work logs.

## Stack
- FastAPI
- SQLAlchemy ORM
- Alembic
- Pydantic
- SQLite (local)
- JWT auth
- Pytest

## Local setup
1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy env template:
   ```bash
   cp .env.example .env
   ```
4. Run migrations:
   ```bash
   alembic upgrade head
   ```
5. Start the app:
   ```bash
   uvicorn app.main:app --reload
   ```
6. Open docs: `http://127.0.0.1:8000/docs`

## Existing Day 1 endpoints
- Auth: `/auth/register`, `/auth/login`, `/auth/me`
- Volunteers CRUD: `/volunteers`
- Events CRUD: `/events`

## New Day 2 endpoints
- Shifts
  - `POST /events/{event_id}/shifts`
  - `GET /events/{event_id}/shifts`
  - `GET /shifts/{id}`
  - `PATCH /shifts/{id}`
  - `DELETE /shifts/{id}`
- Work logs
  - `POST /work-logs`
  - `GET /work-logs/{id}`
  - `PATCH /work-logs/{id}`
  - `DELETE /work-logs/{id}`
- Hours summary
  - `GET /volunteers/{id}/hours`
  - `GET /events/{id}/hours`
- CSV import (admin only)
  - `POST /imports/volunteers`
  - `POST /imports/events`
  - `POST /imports/attendance`

## Worked minutes rule
- `effective_start = max(checked_in_at, shift.start_time)`
- `effective_end = min(checked_out_at, shift.end_time)`
- `worked_minutes = max(0, effective_end - effective_start)`

## Volunteer naming note
- User auth payload uses `full_name`.
- Volunteer payload uses `name` and also accepts `full_name` as alias.

## CSV templates
- `volunteers_import_template_en.csv`
- `events_import_template_en.csv`
- `attendance_import_template_en.csv`

## Tests
```bash
pytest -q
```
