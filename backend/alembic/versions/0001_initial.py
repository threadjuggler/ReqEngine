"""Initial schema: create all four tables.

Revision ID: 0001
Revises:
Create Date: 2026-05-20
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create project_counters, requirements, testcases, and links tables."""
    op.create_table(
        "project_counters",
        sa.Column("project_name", sa.String(100), nullable=False),
        sa.Column("next_number", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("project_name"),
    )

    op.create_table(
        "requirements",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("requirement_number", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.String(100), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.String(500), nullable=False, server_default=""),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("requirement_type", sa.String(80), nullable=False),
        sa.Column("author", sa.String(100), nullable=False),
        sa.Column("last_edited_by", sa.String(100), nullable=False),
        sa.Column(
            "created_on",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "last_edited_on",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("revision", sa.String(30), nullable=False, server_default="0.1"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id"),
    )
    op.create_index("ix_requirements_requirement_number", "requirements", ["requirement_number"])
    op.create_index("ix_requirements_project_id", "requirements", ["project_id"], unique=True)

    op.create_table(
        "testcases",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("project_id", sa.String(100), nullable=False),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("description", sa.String(1000), nullable=False, server_default=""),
        sa.Column("test_state", sa.String(30), nullable=False, server_default="draft"),
        sa.Column("author", sa.String(100), nullable=False),
        sa.Column("last_edited_by", sa.String(100), nullable=False),
        sa.Column(
            "created_on",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "last_edited_on",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("revision", sa.String(30), nullable=False, server_default="0.1"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id"),
    )
    op.create_index("ix_testcases_project_id", "testcases", ["project_id"], unique=True)

    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("project_id", sa.String(100), nullable=False),
        sa.Column("link_type", sa.String(60), nullable=False),
        sa.Column("link_start", sa.Integer(), nullable=False),
        sa.Column("link_destination", sa.Integer(), nullable=False),
        sa.Column(
            "created_on",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "last_edited_on",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["link_start"], ["requirements.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["link_destination"], ["requirements.id"], ondelete="CASCADE"),
        sa.CheckConstraint("link_start <> link_destination", name="ck_link_no_self_ref"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id"),
    )
    op.create_index("ix_links_project_id", "links", ["project_id"], unique=True)


def downgrade() -> None:
    """Drop all four tables in reverse dependency order."""
    op.drop_index("ix_links_project_id", table_name="links")
    op.drop_table("links")
    op.drop_index("ix_testcases_project_id", table_name="testcases")
    op.drop_table("testcases")
    op.drop_index("ix_requirements_project_id", table_name="requirements")
    op.drop_index("ix_requirements_requirement_number", table_name="requirements")
    op.drop_table("requirements")
    op.drop_table("project_counters")
