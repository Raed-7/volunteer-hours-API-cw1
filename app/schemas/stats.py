from pydantic import BaseModel


class StatsResponse(BaseModel):
    total_volunteers: int
    total_events: int
    total_shifts: int
    total_work_logs: int
    total_worked_minutes: int
    total_worked_hours: float