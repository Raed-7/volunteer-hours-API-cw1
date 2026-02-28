from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.volunteer import Volunteer
from app.schemas.volunteer import VolunteerCreate, VolunteerRead, VolunteerUpdate
from app.utils.deps import get_current_user

router = APIRouter(prefix="/volunteers", tags=["volunteers"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=VolunteerRead, status_code=status.HTTP_201_CREATED)
def create_volunteer(payload: VolunteerCreate, db: Session = Depends(get_db)) -> VolunteerRead:
    volunteer = Volunteer(**payload.model_dump())
    db.add(volunteer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Volunteer email already exists")
    db.refresh(volunteer)
    return volunteer


@router.get("", response_model=list[VolunteerRead])
def list_volunteers(db: Session = Depends(get_db)) -> list[VolunteerRead]:
    return db.query(Volunteer).order_by(Volunteer.id).all()


@router.get("/{volunteer_id}", response_model=VolunteerRead)
def get_volunteer(volunteer_id: int, db: Session = Depends(get_db)) -> VolunteerRead:
    volunteer = db.get(Volunteer, volunteer_id)
    if not volunteer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Volunteer not found")
    return volunteer


@router.patch("/{volunteer_id}", response_model=VolunteerRead)
def update_volunteer(volunteer_id: int, payload: VolunteerUpdate, db: Session = Depends(get_db)) -> VolunteerRead:
    volunteer = db.get(Volunteer, volunteer_id)
    if not volunteer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Volunteer not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(volunteer, key, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Volunteer email already exists")
    db.refresh(volunteer)
    return volunteer


@router.delete("/{volunteer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_volunteer(volunteer_id: int, db: Session = Depends(get_db)) -> None:
    volunteer = db.get(Volunteer, volunteer_id)
    if not volunteer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Volunteer not found")
    db.delete(volunteer)
    db.commit()
