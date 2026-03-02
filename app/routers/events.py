from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.event import Event
from app.models.shift import Shift
from app.models.work_log import WorkLog
from app.schemas.event import EventCreate, EventRead, EventUpdate
from app.schemas.work_log import HoursSummary
from app.utils.deps import get_current_user

router = APIRouter(prefix="/events", tags=["events"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate, db: Session = Depends(get_db)) -> EventRead:
    event = Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("", response_model=list[EventRead])
def list_events(db: Session = Depends(get_db)) -> list[EventRead]:
    return db.query(Event).order_by(Event.id).all()


@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)) -> EventRead:
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.get("/{event_id}/hours", response_model=HoursSummary)
def get_event_hours(event_id: int, db: Session = Depends(get_db)) -> HoursSummary:
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    minutes = (
        db.query(func.coalesce(func.sum(WorkLog.worked_minutes), 0))
        .join(Shift, WorkLog.shift_id == Shift.id)
        .filter(Shift.event_id == event_id)
        .scalar()
    )
    return HoursSummary(target_id=event_id, worked_minutes=minutes, worked_hours=round(minutes / 60, 2))


@router.patch("/{event_id}", response_model=EventRead)
def update_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db)) -> EventRead:
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db)) -> None:
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    db.delete(event)
    db.commit()
