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
    created, updated, skipped = 0, 0, 0

    def pick(row: dict[str, str], *keys: str) -> str:
        for key in keys:
            value = row.get(key)
            if value is not None and str(value).strip():
                return str(value).strip()
        return ""

    for row in rows:
        volunteer_no = pick(row, "volunteer_no", "volunteer_id", "volunteer_number", "id")
        name = pick(row, "name", "full_name", "volunteer_name")
        email = pick(row, "email", "mail", "email_address").lower() or None
        phone = pick(row, "phone", "mobile", "phone_number", "contact") or None

        if not name:
            skipped += 1
            continue

        existing = None

        if volunteer_no:
            existing = db.query(Volunteer).filter(Volunteer.volunteer_no == volunteer_no).first()

        if not existing and email:
            existing = db.query(Volunteer).filter(Volunteer.email == email).first()

        if not existing and phone:
            existing = db.query(Volunteer).filter(Volunteer.phone == phone).first()

        if not existing:
            existing = db.query(Volunteer).filter(Volunteer.name == name).first()

        if existing:
            if volunteer_no:
                existing.volunteer_no = volunteer_no
            existing.name = name or existing.name
            if email:
                existing.email = email
            if phone:
                existing.phone = phone
            updated += 1
        else:
            db.add(
                Volunteer(
                    volunteer_no=volunteer_no or None,
                    name=name,
                    email=email,
                    phone=phone,
                )
            )
            created += 1

    db.commit()
    return {"created": created, "updated": updated, "skipped": skipped}

def import_events_csv(db: Session, content: bytes) -> dict[str, int]:
    rows = _decode_csv(content)

    created = 0
    updated = 0
    skipped = 0

    def pick(row: dict[str, str], *keys: str) -> str:
        for key in keys:
            value = row.get(key)
            if value and str(value).strip():
                return str(value).strip()
        return ""

    for row in rows:

        title = pick(row, "event_title", "title", "event_name")
        category = pick(row, "event_category", "category")
        date_raw = pick(row, "event_date", "date")
        location = pick(row, "location", "venue")
        description = pick(row, "description", "details")

        if not title or not date_raw:
            skipped += 1
            continue

        try:
            event_date = datetime.strptime(date_raw, "%d/%m/%Y").date()
        except:
            skipped += 1
            continue

        existing = (
            db.query(Event)
            .filter(Event.title == title, Event.event_date == event_date)
            .first()
        )

        if existing:
            existing.description = description or existing.description
            existing.location = location or existing.location
            updated += 1
        else:
            db.add(
                Event(
                    title=title,
                    description=description,
                    location=location or "Unknown",
                    event_date=event_date,
                )
            )
            created += 1

    db.commit()
    return {"created": created, "updated": updated, "skipped": skipped}

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
