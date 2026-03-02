from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class WorkLog(Base):
    __tablename__ = "work_logs"
    __table_args__ = (UniqueConstraint("volunteer_id", "shift_id", name="uq_work_logs_volunteer_shift"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    volunteer_id: Mapped[int] = mapped_column(ForeignKey("volunteers.id", ondelete="CASCADE"), nullable=False, index=True)
    shift_id: Mapped[int] = mapped_column(ForeignKey("shifts.id", ondelete="CASCADE"), nullable=False, index=True)
    checked_in_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    checked_out_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    worked_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    volunteer = relationship("Volunteer", back_populates="work_logs")
    shift = relationship("Shift", back_populates="work_logs")
