"""add_created_at_to_labels

Revision ID: cc9ca9b2e432
Revises: add_updated_at_deleted_at
Create Date: 2026-06-15 15:01:03.525180

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc9ca9b2e432'
down_revision: Union[str, Sequence[str], None] = 'add_updated_at_deleted_at'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "labels",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_column("labels", "created_at")
