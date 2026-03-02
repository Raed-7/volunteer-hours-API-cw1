from datetime import datetime

from pydantic import BaseModel


class WorkLogBase(BaseModel):
    volunteer_id: int
    shift_id: int
    checked_in_at: datetime
    checked_out_at: datetime


class WorkLogCreate(WorkLogBase):
    pass


class WorkLogUpdate(BaseModel):
    checked_in_at: datetime | None = None
    checked_out_at: datetime | None = None


class WorkLogRead(WorkLogBase):
    id: int
    worked_minutes: int

    model_config = {"from_attributes": True}


class HoursSummary(BaseModel):
    target_id: int
    worked_minutes: int
    worked_hours: float
