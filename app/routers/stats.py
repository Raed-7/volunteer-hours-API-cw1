from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.event import Event
from app.models.shift import Shift
from app.models.volunteer import Volunteer
from app.models.work_log import WorkLog
from app.schemas.stats import StatsResponse
from app.utils.deps import get_current_user

router = APIRouter(prefix="/stats", tags=["stats"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)) -> StatsResponse:
    total_volunteers = db.query(func.count(Volunteer.id)).scalar() or 0
    total_events = db.query(func.count(Event.id)).scalar() or 0
    total_shifts = db.query(func.count(Shift.id)).scalar() or 0
    total_work_logs = db.query(func.count(WorkLog.id)).scalar() or 0
    total_worked_minutes = db.query(func.coalesce(func.sum(WorkLog.worked_minutes), 0)).scalar() or 0

    return StatsResponse(
        total_volunteers=total_volunteers,
        total_events=total_events,
        total_shifts=total_shifts,
        total_work_logs=total_work_logs,
        total_worked_minutes=total_worked_minutes,
        total_worked_hours=round(total_worked_minutes / 60, 2),
    )