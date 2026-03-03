from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.shift import Shift
from app.models.volunteer import Volunteer
from app.models.work_log import WorkLog
from app.schemas.analytics import (
    AwardsResponse,
    AwardVolunteerEntry,
    LeaderboardEntry,
    VolunteerActivityEntry,
    VolunteerSummaryResponse,
)

TIER_A_MIN_HOURS = 20
TIER_B_MIN_HOURS = 15
TIER_C_MIN_HOURS = 1


def _minutes_to_hours(minutes: int) -> float:
    return round(minutes / 60, 2)


def _volunteer_totals_query(db: Session):
    return (
        db.query(
            Volunteer.id.label("volunteer_id"),
            Volunteer.name.label("name"),
            func.coalesce(func.sum(WorkLog.worked_minutes), 0).label("total_minutes"),
        )
        .join(WorkLog, WorkLog.volunteer_id == Volunteer.id)
        .group_by(Volunteer.id, Volunteer.name)
        .order_by(desc("total_minutes"), Volunteer.id)
    )


def get_leaderboard(db: Session, limit: int = 10) -> list[LeaderboardEntry]:
    rows = _volunteer_totals_query(db).limit(limit).all()

    return [
        LeaderboardEntry(
            volunteer_id=row.volunteer_id,
            name=row.name,
            total_minutes=row.total_minutes,
            total_hours=_minutes_to_hours(row.total_minutes),
        )
        for row in rows
    ]


def get_awards(db: Session) -> AwardsResponse:
    rows = _volunteer_totals_query(db).all()

    tier_a: list[AwardVolunteerEntry] = []
    tier_b: list[AwardVolunteerEntry] = []
    tier_c: list[AwardVolunteerEntry] = []

    for row in rows:
        total_hours = _minutes_to_hours(row.total_minutes)
        entry = AwardVolunteerEntry(
            volunteer_id=row.volunteer_id,
            name=row.name,
            total_minutes=row.total_minutes,
            total_hours=total_hours,
        )

        if total_hours >= TIER_A_MIN_HOURS:
            tier_a.append(entry)
        elif total_hours >= TIER_B_MIN_HOURS:
            tier_b.append(entry)
        elif total_hours >= TIER_C_MIN_HOURS:
            tier_c.append(entry)

    return AwardsResponse(tier_a=tier_a, tier_b=tier_b, tier_c=tier_c)


def get_volunteer_summary(db: Session, volunteer_id: int, recent_limit: int = 5) -> VolunteerSummaryResponse | None:
    volunteer = db.get(Volunteer, volunteer_id)
    if not volunteer:
        return None

    totals = (
        db.query(
            func.coalesce(func.sum(WorkLog.worked_minutes), 0).label("total_minutes"),
            func.count(WorkLog.id).label("total_shifts_worked"),
            func.count(func.distinct(Shift.event_id)).label("total_events_worked"),
        )
        .join(Shift, WorkLog.shift_id == Shift.id)
        .filter(WorkLog.volunteer_id == volunteer_id)
        .one()
    )

    activity_rows = (
        db.query(
            Event.id.label("event_id"),
            Event.title.label("event_title"),
            Shift.id.label("shift_id"),
            Shift.name.label("shift_name"),
            WorkLog.checked_in_at.label("checked_in_at"),
            WorkLog.checked_out_at.label("checked_out_at"),
            WorkLog.worked_minutes.label("worked_minutes"),
        )
        .join(Shift, WorkLog.shift_id == Shift.id)
        .join(Event, Shift.event_id == Event.id)
        .filter(WorkLog.volunteer_id == volunteer_id)
        .order_by(desc(WorkLog.checked_in_at))
        .limit(recent_limit)
        .all()
    )

    recent_activity = [
        VolunteerActivityEntry(
            event_id=row.event_id,
            event_title=row.event_title,
            shift_id=row.shift_id,
            shift_name=row.shift_name,
            checked_in_at=row.checked_in_at,
            checked_out_at=row.checked_out_at,
            worked_minutes=row.worked_minutes,
            worked_hours=_minutes_to_hours(row.worked_minutes),
        )
        for row in activity_rows
    ]

    total_minutes = totals.total_minutes or 0
    total_shifts_worked = totals.total_shifts_worked or 0
    total_events_worked = totals.total_events_worked or 0

    return VolunteerSummaryResponse(
        volunteer_id=volunteer.id,
        name=volunteer.name,
        total_events_worked=total_events_worked,
        total_shifts_worked=total_shifts_worked,
        total_minutes=total_minutes,
        total_hours=_minutes_to_hours(total_minutes),
        recent_activity=recent_activity,
    )