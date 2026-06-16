"""add_created_at_to_workspace members

Revision ID: b89dfffcc1b4
Revises: cc9ca9b2e432
Create Date: 2026-06-16 15:32:09.847543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b89dfffcc1b4'
down_revision: Union[str, Sequence[str], None] = 'cc9ca9b2e432'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "workspace_members",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_column("workspace_members", "created_at")
