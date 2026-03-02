import csv
import io
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.shift import Shift
from app.models.volunteer import Volunteer
from app.models.work_log import WorkLog
from app.services.hours_service import calculate_worked_minutes


def _decode_csv(content: bytes) -> list[dict[str, str]]:
    text = content.decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def import_volunteers_csv(db: Session, content: bytes) -> dict[str, int]:
    rows = _decode_csv(content)
    created, updated = 0, 0
    for row in rows:
        email = (row.get("email") or "").strip().lower()
        if not email:
            continue
        name = (row.get("name") or row.get("full_name") or "").strip()
        phone = (row.get("phone") or "").strip() or None
        existing = db.query(Volunteer).filter(Volunteer.email == email).first()
        if existing:
            existing.name = name or existing.name
            existing.phone = phone
            updated += 1
        else:
            db.add(Volunteer(name=name, email=email, phone=phone))
            created += 1
    db.commit()
    return {"created": created, "updated": updated}


def import_events_csv(db: Session, content: bytes) -> dict[str, int]:
    rows = _decode_csv(content)
    created, updated = 0, 0
    for row in rows:
        title = (row.get("title") or "").strip()
        location = (row.get("location") or "").strip()
        event_date_raw = (row.get("event_date") or "").strip()
        if not title or not location or not event_date_raw:
            continue
        event_date_value = date.fromisoformat(event_date_raw)

        existing = (
            db.query(Event)
            .filter(Event.title == title, Event.location == location, Event.event_date == event_date_value)
            .first()
        )
        description = (row.get("description") or "").strip() or None
        if existing:
            existing.description = description
            updated += 1
        else:
            db.add(Event(title=title, description=description, location=location, event_date=event_date_value))
            created += 1
    db.commit()
    return {"created": created, "updated": updated}


def import_attendance_csv(db: Session, content: bytes) -> dict[str, int]:
    rows = _decode_csv(content)
    created, updated = 0, 0
    for row in rows:
        volunteer_email = (row.get("volunteer_email") or "").strip().lower()
        shift_id = int(row.get("shift_id") or 0)
        checked_in_at_raw = (row.get("checked_in_at") or "").strip()
        checked_out_at_raw = (row.get("checked_out_at") or "").strip()
        if not volunteer_email or not shift_id or not checked_in_at_raw or not checked_out_at_raw:
            continue

        volunteer = db.query(Volunteer).filter(Volunteer.email == volunteer_email).first()
        shift = db.get(Shift, shift_id)
        if not volunteer or not shift:
            continue

        checked_in_at = datetime.fromisoformat(checked_in_at_raw)
        checked_out_at = datetime.fromisoformat(checked_out_at_raw)
        worked_minutes = calculate_worked_minutes(
            shift_start=shift.start_time,
            shift_end=shift.end_time,
            checked_in_at=checked_in_at,
            checked_out_at=checked_out_at,
        )

        existing = db.query(WorkLog).filter(WorkLog.volunteer_id == volunteer.id, WorkLog.shift_id == shift.id).first()
        if existing:
            existing.checked_in_at = checked_in_at
            existing.checked_out_at = checked_out_at
            existing.worked_minutes = worked_minutes
            updated += 1
        else:
            db.add(
                WorkLog(
                    volunteer_id=volunteer.id,
                    shift_id=shift.id,
                    checked_in_at=checked_in_at,
                    checked_out_at=checked_out_at,
                    worked_minutes=worked_minutes,
                )
            )
            created += 1
    db.commit()
    return {"created": created, "updated": updated}
