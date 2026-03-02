from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.event import Event
from app.models.shift import Shift
from app.schemas.shift import ShiftCreate, ShiftRead, ShiftUpdate
from app.services.hours_service import validate_shift_window
from app.utils.deps import get_current_user

router = APIRouter(tags=["shifts"], dependencies=[Depends(get_current_user)])


@router.post("/events/{event_id}/shifts", response_model=ShiftRead, status_code=status.HTTP_201_CREATED)
def create_shift(event_id: int, payload: ShiftCreate, db: Session = Depends(get_db)) -> ShiftRead:
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    try:
        validate_shift_window(payload.start_time, payload.end_time)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    shift = Shift(event_id=event_id, **payload.model_dump())
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift


@router.get("/events/{event_id}/shifts", response_model=list[ShiftRead])
def list_event_shifts(event_id: int, db: Session = Depends(get_db)) -> list[ShiftRead]:
    return db.query(Shift).filter(Shift.event_id == event_id).order_by(Shift.id).all()


@router.get("/shifts/{shift_id}", response_model=ShiftRead)
def get_shift(shift_id: int, db: Session = Depends(get_db)) -> ShiftRead:
    shift = db.get(Shift, shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift


@router.patch("/shifts/{shift_id}", response_model=ShiftRead)
def update_shift(shift_id: int, payload: ShiftUpdate, db: Session = Depends(get_db)) -> ShiftRead:
    shift = db.get(Shift, shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(shift, key, value)

    try:
        validate_shift_window(shift.start_time, shift.end_time)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    db.commit()
    db.refresh(shift)
    return shift


@router.delete("/shifts/{shift_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shift(shift_id: int, db: Session = Depends(get_db)) -> None:
    shift = db.get(Shift, shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    db.delete(shift)
    db.commit()
