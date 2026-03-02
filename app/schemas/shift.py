from datetime import datetime

from pydantic import BaseModel, Field


class ShiftBase(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    start_time: datetime
    end_time: datetime


class ShiftCreate(ShiftBase):
    pass


class ShiftUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None


class ShiftRead(ShiftBase):
    id: int
    event_id: int

    model_config = {"from_attributes": True}
