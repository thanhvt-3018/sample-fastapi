"""add_updated_at_deleted_at

Revision ID: add_updated_at_deleted_at
Revises: 4b85d6846300
Create Date: 2026-06-11 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "add_updated_at_deleted_at"
down_revision: Union[str, Sequence[str], None] = "4b85d6846300"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    tables = [
        "users",
        "workspaces",
        "workspace_members",
        "projects",
        "tasks",
        "labels",
        "comments",
    ]

    for table in tables:
        op.add_column(
            table,
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("now()"),
            ),
        )
        op.add_column(
            table,
            sa.Column(
                "deleted_at",
                sa.DateTime(),
                nullable=True,
                server_default=None,
            ),
        )


def downgrade() -> None:
    tables = [
        "users",
        "workspaces",
        "workspace_members",
        "projects",
        "tasks",
        "labels",
        "comments",
    ]

    for table in tables:
        op.drop_column(table, "deleted_at")
        op.drop_column(table, "updated_at")
