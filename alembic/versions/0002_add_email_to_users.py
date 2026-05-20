"""add email column to users

Revision ID: 0002_add_email
Revises: 0001_initial
Create Date: 2026-05-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_add_email"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("email", sa.String(255), nullable=False, server_default=""),
    )
    op.execute(
        "UPDATE users SET email = CONCAT(name, '@reqengine.local') WHERE email = ''"
    )
    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(255),
        existing_nullable=False,
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("users", "email")
