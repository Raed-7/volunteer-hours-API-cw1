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

## Setup

1. Create a virtual environment and activate it.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create environment file:
   ```bash
   cp .env.example .env
   ```

## Run migrations

```bash
alembic upgrade head
```

## Run the API locally

```bash
uvicorn app.main:app --reload
```

API docs available at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Run tests

```bash
pytest -q
```

## Notes

- Shifts, work logs, analytics, and CSV import are intentionally postponed for later milestones.
