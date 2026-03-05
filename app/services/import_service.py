import csv
import io
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.shift import Shift
from app.models.volunteer import Volunteer
from app.models.work_log import WorkLog
from app.services.hours_service import calculate_worked_minutes


def _decode_csv(content: bytes) -> list[dict[str, str]]:
    text = content.decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))

def _norm_key(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "_")


def _get_any(row: dict[str, str], *keys: str) -> str:
    norm_row = {_norm_key(k): (v or "").strip() for k, v in row.items()}
    for k in keys:
        v = norm_row.get(_norm_key(k), "")
        if v:
            return v
    return ""


def _parse_date_flexible(raw: str) -> date | None:
    raw = (raw or "").strip()
    if not raw:
        return None

    # try ISO first: YYYY-MM-DD
    try:
        return date.fromisoformat(raw)
    except ValueError:
        pass

    # try DD/MM/YYYY
    try:
        return datetime.strptime(raw, "%d/%m/%Y").date()
    except ValueError:
        return None


def _parse_float(raw: str) -> float | None:
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None

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
    created, updated, skipped = 0, 0, 0

    for row in rows:
        # accept lots of column name variations
        title = _get_any(row, "title", "event_title", "name", "event_name")
        location = _get_any(row, "location", "venue", "place")
        description = _get_any(row, "description", "details", "notes")
        event_date_raw = _get_any(row, "event_date", "date")

        event_date_value = _parse_date_flexible(event_date_raw)

        if not title or not event_date_value:
            skipped += 1
            continue

        # if location missing, default it (because your Event model requires it)
        if not location:
            location = "Imported"

        existing = (
            db.query(Event)
            .filter(Event.title == title, Event.event_date == event_date_value)
            .first()
        )

        if existing:
            # update basic fields
            existing.location = location or existing.location
            existing.description = description or existing.description
            updated += 1
        else:
            db.add(
                Event(
                    title=title,
                    location=location,
                    description=description or None,
                    event_date=event_date_value,
                )
            )
            created += 1

    db.commit()
    return {"created": created, "updated": updated, "skipped": skipped}

def import_attendance_csv(db: Session, content: bytes) -> dict[str, int]:
    rows = _decode_csv(content)
    created, updated, skipped = 0, 0, 0

    for row in rows:
        # ---------- FORMAT A: original worklog format ----------
        volunteer_email = _get_any(row, "volunteer_email", "email")
        shift_id_raw = _get_any(row, "shift_id")
        checked_in_at_raw = _get_any(row, "checked_in_at")
        checked_out_at_raw = _get_any(row, "checked_out_at")

        if shift_id_raw and checked_in_at_raw and checked_out_at_raw:
            shift_id = int(shift_id_raw or 0)
            volunteer = db.query(Volunteer).filter(Volunteer.email == volunteer_email.lower()).first() if volunteer_email else None
            shift = db.get(Shift, shift_id)

            if not volunteer or not shift:
                skipped += 1
                continue

            checked_in_at = datetime.fromisoformat(checked_in_at_raw)
            checked_out_at = datetime.fromisoformat(checked_out_at_raw)

            worked_minutes = calculate_worked_minutes(
                shift_start=shift.start_time,
                shift_end=shift.end_time,
                checked_in_at=checked_in_at,
                checked_out_at=checked_out_at,
            )

            existing = db.query(WorkLog).filter(
                WorkLog.volunteer_id == volunteer.id,
                WorkLog.shift_id == shift.id
            ).first()

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

            continue  # done with this row

        # ---------- FORMAT B: spreadsheet format ----------
        full_name = _get_any(row, "full_name", "name", "volunteer_name")
        event_category = _get_any(row, "event_category", "category")
        event_title = _get_any(row, "event_title", "title")  # might be missing
        event_date_value = _parse_date_flexible(_get_any(row, "event_date", "date"))
        hours_value = _parse_float(_get_any(row, "hours", "worked_hours", "time"))

        if not full_name or not event_date_value or not hours_value or hours_value <= 0:
            skipped += 1
            continue

        # find volunteer by name (fallback)
        volunteer = db.query(Volunteer).filter(Volunteer.name == full_name).first()
        if not volunteer:
            # optionally auto-create volunteer if missing
            volunteer = Volunteer(name=full_name, email=None, phone=None)
            db.add(volunteer)
            db.commit()
            db.refresh(volunteer)

        # choose an event title
        title = event_title or (event_category or "Imported Event")

        # find or create event
        event = db.query(Event).filter(Event.title == title, Event.event_date == event_date_value).first()
        if not event:
            event = Event(
                title=title,
                location="Imported",
                description="Imported from attendance spreadsheet",
                event_date=event_date_value,
            )
            db.add(event)
            db.commit()
            db.refresh(event)

        # find or create shift for this event/date/hours
        start_time = datetime.combine(event_date_value, datetime.min.time()).replace(hour=9, minute=0)
        end_time = start_time + timedelta(minutes=int(hours_value * 60))

        shift = db.query(Shift).filter(
            Shift.event_id == event.id,
            Shift.start_time == start_time,
            Shift.end_time == end_time
        ).first()

        if not shift:
            shift = Shift(
                event_id=event.id,
                name="Imported shift",
                description="Auto-created from attendance import",
                start_time=start_time,
                end_time=end_time,
            )
            db.add(shift)
            db.commit()
            db.refresh(shift)

        worked_minutes = calculate_worked_minutes(
            shift_start=shift.start_time,
            shift_end=shift.end_time,
            checked_in_at=start_time,
            checked_out_at=end_time,
        )

        existing = db.query(WorkLog).filter(
            WorkLog.volunteer_id == volunteer.id,
            WorkLog.shift_id == shift.id
        ).first()

        if existing:
            existing.checked_in_at = start_time
            existing.checked_out_at = end_time
            existing.worked_minutes = worked_minutes
            updated += 1
        else:
            db.add(
                WorkLog(
                    volunteer_id=volunteer.id,
                    shift_id=shift.id,
                    checked_in_at=start_time,
                    checked_out_at=end_time,
                    worked_minutes=worked_minutes,
                )
            )
            created += 1

    db.commit()
    return {"created": created, "updated": updated, "skipped": skipped}
