from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.shift import Shift
from app.models.volunteer import Volunteer
from app.models.work_log import WorkLog
from app.schemas.work_log import WorkLogCreate, WorkLogRead, WorkLogUpdate
from app.services.hours_service import calculate_worked_minutes
from app.utils.deps import get_current_user

router = APIRouter(prefix="/work-logs", tags=["work-logs"], dependencies=[Depends(get_current_user)])


def _compute_minutes(shift: Shift, checked_in_at, checked_out_at) -> int:
    try:
        return calculate_worked_minutes(
            shift_start=shift.start_time,
            shift_end=shift.end_time,
            checked_in_at=checked_in_at,
            checked_out_at=checked_out_at,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("", response_model=WorkLogRead, status_code=status.HTTP_201_CREATED)
def create_work_log(payload: WorkLogCreate, db: Session = Depends(get_db)) -> WorkLogRead:
    volunteer = db.get(Volunteer, payload.volunteer_id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")

    shift = db.get(Shift, payload.shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    worked_minutes = _compute_minutes(shift, payload.checked_in_at, payload.checked_out_at)
    log = WorkLog(**payload.model_dump(), worked_minutes=worked_minutes)
    db.add(log)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Work log already exists for this volunteer and shift")
    db.refresh(log)
    return log


@router.get("/{work_log_id}", response_model=WorkLogRead)
def get_work_log(work_log_id: int, db: Session = Depends(get_db)) -> WorkLogRead:
    log = db.get(WorkLog, work_log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Work log not found")
    return log


@router.patch("/{work_log_id}", response_model=WorkLogRead)
def update_work_log(work_log_id: int, payload: WorkLogUpdate, db: Session = Depends(get_db)) -> WorkLogRead:
    log = db.get(WorkLog, work_log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Work log not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(log, key, value)

    shift = db.get(Shift, log.shift_id)
    log.worked_minutes = _compute_minutes(shift, log.checked_in_at, log.checked_out_at)

    db.commit()
    db.refresh(log)
    return log


@router.delete("/{work_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_work_log(work_log_id: int, db: Session = Depends(get_db)) -> None:
    log = db.get(WorkLog, work_log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Work log not found")
    db.delete(log)
    db.commit()
