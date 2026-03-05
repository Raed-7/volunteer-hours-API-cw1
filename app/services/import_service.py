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

    created = 0
    skipped = 0

    for row in rows:

        name = row.get("full_name", "").strip()
        category = row.get("event_category", "").strip()
        date_raw = row.get("event_date", "").strip()
        hours_raw = row.get("hours", "").strip()

        if not name or not date_raw:
            skipped += 1
            continue

        try:
            event_date = datetime.strptime(date_raw, "%d/%m/%Y").date()
        except:
            skipped += 1
            continue

        try:
            hours = float(hours_raw)
        except:
            skipped += 1
            continue

        volunteer = db.query(Volunteer).filter(Volunteer.name == name).first()

        if not volunteer:
            skipped += 1
            continue

        event = (
            db.query(Event)
            .filter(Event.event_date == event_date)
            .first()
        )

        if not event:
            skipped += 1
            continue

        minutes = int(hours * 60)

        work_log = WorkLog(
            volunteer_id=volunteer.id,
            shift_id=None,
            worked_minutes=minutes,
        )

        db.add(work_log)
        created += 1

    db.commit()

    return {
        "created": created,
        "skipped": skipped,
    }
