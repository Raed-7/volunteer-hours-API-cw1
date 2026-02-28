# Volunteer Hours Management API

A coursework-ready backend API for managing volunteers and events. This first milestone includes authentication, role support, and protected CRUD endpoints for volunteers and events.

## Tech stack

- Python + FastAPI
- SQLAlchemy ORM
- Alembic migrations
- Pydantic schemas
- SQLite (local development)
- JWT authentication
- Pytest

## Features implemented today

- User registration/login/me endpoints
- JWT-based authentication
- Role support (`admin`, `organiser`)
- Protected volunteer CRUD endpoints
- Protected event CRUD endpoints
- Alembic initial migration for `users`, `volunteers`, `events`

## Project structure

```text
app/
  core/
  db/
  models/
  routers/
  schemas/
  services/
  utils/
  main.py
alembic/
tests/
```

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create your local environment file:
   ```bash
   cp .env.example .env
   ```
4. Run database migrations before starting the app:
   ```bash
   alembic upgrade head
   ```
5. Start the API server:
   ```bash
   uvicorn app.main:app --reload
   ```
6. Open API docs:
   - `http://127.0.0.1:8000/docs`
   - `http://127.0.0.1:8000/redoc`

## Run tests

```bash
pytest -q
```

## Field naming note

- Auth user payload uses `full_name`.
- Volunteer payload uses `name`, and also accepts `full_name` as an input alias for compatibility.

## Notes

- Shifts, work logs, analytics, and CSV import are intentionally postponed for later milestones.
