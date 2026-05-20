"""Step 2: add project + document tables; add project_id_number FK to existing tables.

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Drop & recreate requirement/testcase/link/project_counter; add project & document."""
    # Drop existing tables in reverse FK order (wipe per decision D6)
    op.drop_index("ix_links_project_id", table_name="links")
    op.drop_table("links")
    op.drop_index("ix_testcases_project_id", table_name="testcases")
    op.drop_table("testcases")
    op.drop_index("ix_requirements_project_id", table_name="requirements")
    op.drop_index("ix_requirements_requirement_number", table_name="requirements")
    op.drop_table("requirements")
    op.drop_table("project_counters")

    # Create project table
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("project_name", sa.String(120), nullable=False),
        sa.Column(
            "user_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[10, 20]",
        ),
        sa.Column(
            "created_on",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_name"),
    )

    # Recreate project_counters
    op.create_table(
        "project_counters",
        sa.Column("project_name", sa.String(100), nullable=False),
        sa.Column("next_number", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("project_name"),
    )

    # Recreate requirements with project_id_number FK
    op.create_table(
        "requirements",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("requirement_number", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.String(100), nullable=False),
        sa.Column("project_id_number", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(["project_id_number"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id"),
    )
    op.create_index("ix_requirements_requirement_number", "requirements", ["requirement_number"])
    op.create_index("ix_requirements_project_id", "requirements", ["project_id"], unique=True)
    op.create_index(
        "ix_requirements_project_id_number", "requirements", ["project_id_number"]
    )

    # Recreate testcases with project_id_number FK
    op.create_table(
        "testcases",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("project_id", sa.String(100), nullable=False),
        sa.Column("project_id_number", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(["project_id_number"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id"),
    )
    op.create_index("ix_testcases_project_id", "testcases", ["project_id"], unique=True)
    op.create_index("ix_testcases_project_id_number", "testcases", ["project_id_number"])

    # Recreate links with project_id_number FK
    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("project_id", sa.String(100), nullable=False),
        sa.Column("project_id_number", sa.Integer(), nullable=False),
        sa.Column("link_type", sa.String(60), nullable=False),
        sa.Column("link_start_kind", sa.String(20), nullable=False),
        sa.Column("link_start", sa.Integer(), nullable=False),
        sa.Column("link_destination_kind", sa.String(20), nullable=False),
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
        sa.CheckConstraint(
            "NOT (link_start_kind = link_destination_kind AND link_start = link_destination)",
            name="ck_link_no_self_ref",
        ),
        sa.ForeignKeyConstraint(["project_id_number"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id"),
    )
    op.create_index("ix_links_project_id", "links", ["project_id"], unique=True)
    op.create_index("ix_links_project_id_number", "links", ["project_id_number"])

    # Create documents table
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("project_id", sa.String(100), nullable=False),
        sa.Column("project_id_number", sa.Integer(), nullable=False),
        sa.Column(
            "created_on",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "last_edit_on",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("author", sa.String(100), nullable=False),
        sa.Column("last_change_by", sa.String(100), nullable=False),
        sa.Column(
            "document_content",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default='{"type": "doc", "content": []}',
        ),
        sa.ForeignKeyConstraint(["project_id_number"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id"),
    )
    op.create_index("ix_documents_project_id", "documents", ["project_id"], unique=True)
    op.create_index("ix_documents_project_id_number", "documents", ["project_id_number"])


def downgrade() -> None:
    """Reverse upgrade: drop new tables and restore original Step 1 schema."""
    # Drop Step 2 tables
    op.drop_index("ix_documents_project_id_number", table_name="documents")
    op.drop_index("ix_documents_project_id", table_name="documents")
    op.drop_table("documents")

    op.drop_index("ix_links_project_id_number", table_name="links")
    op.drop_index("ix_links_project_id", table_name="links")
    op.drop_table("links")

    op.drop_index("ix_testcases_project_id_number", table_name="testcases")
    op.drop_index("ix_testcases_project_id", table_name="testcases")
    op.drop_table("testcases")

    op.drop_index("ix_requirements_project_id_number", table_name="requirements")
    op.drop_index("ix_requirements_project_id", table_name="requirements")
    op.drop_index("ix_requirements_requirement_number", table_name="requirements")
    op.drop_table("requirements")

    op.drop_table("project_counters")
    op.drop_table("projects")

    # Restore Step 1 schema (without project_id_number)
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
        sa.Column("link_start_kind", sa.String(20), nullable=False),
        sa.Column("link_start", sa.Integer(), nullable=False),
        sa.Column("link_destination_kind", sa.String(20), nullable=False),
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
        sa.CheckConstraint(
            "NOT (link_start_kind = link_destination_kind AND link_start = link_destination)",
            name="ck_link_no_self_ref",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id"),
    )
    op.create_index("ix_links_project_id", "links", ["project_id"], unique=True)
