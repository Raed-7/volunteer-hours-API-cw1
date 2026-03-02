"""add shifts and work logs

Revision ID: 20240301_0002
Revises: 20240227_0001
Create Date: 2024-03-01 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20240301_0002"
down_revision: Union[str, None] = "20240227_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "shifts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_shifts_id"), "shifts", ["id"], unique=False)
    op.create_index(op.f("ix_shifts_event_id"), "shifts", ["event_id"], unique=False)

    op.create_table(
        "work_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("volunteer_id", sa.Integer(), nullable=False),
        sa.Column("shift_id", sa.Integer(), nullable=False),
        sa.Column("checked_in_at", sa.DateTime(), nullable=False),
        sa.Column("checked_out_at", sa.DateTime(), nullable=False),
        sa.Column("worked_minutes", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["shift_id"], ["shifts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["volunteer_id"], ["volunteers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("volunteer_id", "shift_id", name="uq_work_logs_volunteer_shift"),
    )
    op.create_index(op.f("ix_work_logs_id"), "work_logs", ["id"], unique=False)
    op.create_index(op.f("ix_work_logs_shift_id"), "work_logs", ["shift_id"], unique=False)
    op.create_index(op.f("ix_work_logs_volunteer_id"), "work_logs", ["volunteer_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_work_logs_volunteer_id"), table_name="work_logs")
    op.drop_index(op.f("ix_work_logs_shift_id"), table_name="work_logs")
    op.drop_index(op.f("ix_work_logs_id"), table_name="work_logs")
    op.drop_table("work_logs")

    op.drop_index(op.f("ix_shifts_event_id"), table_name="shifts")
    op.drop_index(op.f("ix_shifts_id"), table_name="shifts")
    op.drop_table("shifts")
