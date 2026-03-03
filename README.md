# Volunteer Hours Management API

A coursework-ready backend API for managing volunteers, events, shifts, work logs, CSV imports, and worked-hours analytics.

This project is designed for event organisers who need a structured backend system to:

* manage volunteers and events
* create shifts for events
* record volunteer work logs
* calculate official worked hours
* import existing CSV data
* view analytics such as leaderboard, awards, and volunteer summaries

## Tech stack

* Python + FastAPI
* SQLAlchemy ORM
* Alembic migrations
* Pydantic schemas
* SQLite (local development)
* JWT authentication
* Pytest

## Features

### Authentication and roles

* User registration
* User login
* Current user endpoint
* JWT-based authentication
* Role support:

  * `admin`
  * `organiser`

### Volunteer management

* Create volunteer
* List volunteers
* Get volunteer by ID
* Update volunteer
* Delete volunteer
* Volunteer total hours summary

### Event management

* Create event
* List events
* Get event by ID
* Update event
* Delete event
* Event total hours summary

### Shift management

* Create shifts for events
* List shifts for an event
* Get shift by ID
* Update shift
* Delete shift

### Work logs

* Create work logs
* Get work log by ID
* Update work log
* Delete work log
* Automatic `worked_minutes` calculation based on:

  * shift start/end
  * volunteer check-in/check-out
* Validation for invalid work log times
* Duplicate work log prevention for the same volunteer and shift

### CSV import

Admin-only CSV import endpoints:

* `POST /imports/volunteers`
* `POST /imports/events`
* `POST /imports/attendance`

### Analytics

* `GET /analytics/leaderboard`
* `GET /analytics/awards`
* `GET /analytics/volunteers/{volunteer_id}/summary`

## Worked-hours logic

Worked time is calculated from `checked_in_at` and `checked_out_at`, capped to the shift boundaries.

The logic is:

* `effective_start = max(checked_in_at, shift.start_time)`
* `effective_end = min(checked_out_at, shift.end_time)`
* `worked_minutes = max(0, effective_end - effective_start)`

This prevents over-counting outside the planned shift window.

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
docs/
tests/
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Raed-7/volunteer-hours-API-cw1.git
cd volunteer-hours-API-cw1
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

On Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create your local environment file

```bash
copy .env.example .env
```

### 5. Set Python path for the current shell

On Windows PowerShell:

```bash
$env:PYTHONPATH = (Get-Location).Path
```

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Start the API server

```bash
uvicorn app.main:app --reload
```

### 8. Open API docs

* `http://127.0.0.1:8000/docs`
* `http://127.0.0.1:8000/redoc`

## Running tests

```bash
pytest -q
```

## Importing CSV data

The API supports CSV uploads through admin-only endpoints.

Use Swagger at `/docs`, authorize as an `admin`, then upload:

* `volunteers_import_template_en.csv`
* `events_import_template_en.csv`
* `attendance_import_template_en.csv`

Available endpoints:

* `POST /imports/volunteers`
* `POST /imports/events`
* `POST /imports/attendance`

## Main route groups

* `/auth`
* `/volunteers`
* `/events`
* `/shifts`
* `/work-logs`
* `/imports`
* `/analytics`

## Field naming note

* Auth registration currently uses `full_name`
* Volunteer payload currently uses `name`

This difference is kept for compatibility with the current implementation.

## Notes

* The base URL `/` may return `404 Not Found`; the main interactive interface is available at `/docs`
* Import endpoints are admin-protected
* Analytics results are most useful after importing volunteer, event, and attendance data
