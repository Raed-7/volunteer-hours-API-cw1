"""make volunteer import flexible"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Keep these values from your generated file
revision: str = '0a3138adfccd'
down_revision: Union[str, None] = '20240301_0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("volunteers", schema=None) as batch_op:
        batch_op.add_column(sa.Column("volunteer_no", sa.String(length=100), nullable=True))
        batch_op.alter_column("email", existing_type=sa.String(length=255), nullable=True)
        batch_op.create_index(batch_op.f("ix_volunteers_volunteer_no"), ["volunteer_no"], unique=False)
        batch_op.create_unique_constraint("uq_volunteers_volunteer_no", ["volunteer_no"])


def downgrade() -> None:
    with op.batch_alter_table("volunteers", schema=None) as batch_op:
        batch_op.drop_constraint("uq_volunteers_volunteer_no", type_="unique")
        batch_op.drop_index(batch_op.f("ix_volunteers_volunteer_no"))
        batch_op.alter_column("email", existing_type=sa.String(length=255), nullable=False)
        batch_op.drop_column("volunteer_no")