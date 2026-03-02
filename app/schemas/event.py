from datetime import date

from pydantic import BaseModel, Field


class EventBase(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    description: str | None = None
    location: str = Field(min_length=2, max_length=255)
    event_date: date


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    location: str | None = Field(default=None, min_length=2, max_length=255)
    event_date: date | None = None


class EventRead(EventBase):
    id: int

    model_config = {"from_attributes": True}
