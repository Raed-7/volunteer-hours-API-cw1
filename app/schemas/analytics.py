from datetime import datetime

from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    volunteer_id: int
    name: str
    total_minutes: int
    total_hours: float


class AwardVolunteerEntry(BaseModel):
    volunteer_id: int
    name: str
    total_minutes: int
    total_hours: float


class AwardsResponse(BaseModel):
    tier_a: list[AwardVolunteerEntry]
    tier_b: list[AwardVolunteerEntry]
    tier_c: list[AwardVolunteerEntry]


class VolunteerActivityEntry(BaseModel):
    event_id: int
    event_title: str
    shift_id: int
    shift_name: str
    checked_in_at: datetime
    checked_out_at: datetime
    worked_minutes: int
    worked_hours: float


class VolunteerSummaryResponse(BaseModel):
    volunteer_id: int
    name: str
    total_events_worked: int
    total_shifts_worked: int
    total_minutes: int
    total_hours: float
    recent_activity: list[VolunteerActivityEntry]