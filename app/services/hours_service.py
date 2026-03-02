from datetime import datetime


def validate_shift_window(start_time: datetime, end_time: datetime) -> None:
    if end_time <= start_time:
        raise ValueError("Shift end_time must be after start_time")


def calculate_worked_minutes(
    *,
    shift_start: datetime,
    shift_end: datetime,
    checked_in_at: datetime,
    checked_out_at: datetime,
) -> int:
    if checked_out_at < checked_in_at:
        raise ValueError("checked_out_at must be after checked_in_at")

    effective_start = max(checked_in_at, shift_start)
    effective_end = min(checked_out_at, shift_end)

    if effective_end <= effective_start:
        return 0

    delta = effective_end - effective_start
    return int(delta.total_seconds() // 60)
