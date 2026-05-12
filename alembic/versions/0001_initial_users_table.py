"""initial users table

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("hashed_password", sa.String(200), nullable=False),
        sa.Column(
            "log_in_active",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("last_log_in", sa.DateTime, nullable=True),
        sa.CheckConstraint("log_in_active IN (0, 1)", name="ck_users_log_in_active"),
        sa.UniqueConstraint("id", name="uq_users_id"),
        mysql_engine="InnoDB",
    )
    op.execute("ALTER TABLE users AUTO_INCREMENT = 10000")


def downgrade() -> None:
    op.drop_table("users")
