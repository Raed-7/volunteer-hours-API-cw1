from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.import_service import import_attendance_csv, import_events_csv, import_volunteers_csv
from app.utils.deps import get_current_admin

router = APIRouter(prefix="/imports", tags=["imports"], dependencies=[Depends(get_current_admin)])


@router.post("/volunteers")
async def import_volunteers(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict[str, int]:
    return import_volunteers_csv(db, await file.read())


@router.post("/events")
async def import_events(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict[str, int]:
    return import_events_csv(db, await file.read())


@router.post("/attendance")
async def import_attendance(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict[str, int]:
    return import_attendance_csv(db, await file.read())
