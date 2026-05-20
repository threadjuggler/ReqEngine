"""Polymorphic links: links can now point at requirements or testcases.

Adds link_start_kind and link_destination_kind columns (default 'requirement'),
drops the old FK constraints to requirements.id (since destinations may now be
testcases), and replaces the self-link CHECK to consider kind+id together.

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-20
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add kind columns to links, drop old FKs, replace the self-link CHECK."""
    with op.batch_alter_table("links") as batch:
        batch.add_column(
            sa.Column(
                "link_start_kind",
                sa.String(20),
                nullable=False,
                server_default="requirement",
            )
        )
        batch.add_column(
            sa.Column(
                "link_destination_kind",
                sa.String(20),
                nullable=False,
                server_default="requirement",
            )
        )
        batch.drop_constraint("links_link_start_fkey", type_="foreignkey")
        batch.drop_constraint("links_link_destination_fkey", type_="foreignkey")
        batch.drop_constraint("ck_link_no_self_ref", type_="check")
        batch.create_check_constraint(
            "ck_link_no_self_ref",
            "NOT (link_start_kind = link_destination_kind AND link_start = link_destination)",
        )


def downgrade() -> None:
    """Restore the requirement-only schema (assumes no testcase links exist)."""
    with op.batch_alter_table("links") as batch:
        batch.drop_constraint("ck_link_no_self_ref", type_="check")
        batch.create_check_constraint(
            "ck_link_no_self_ref", "link_start <> link_destination"
        )
        batch.create_foreign_key(
            "links_link_start_fkey",
            "requirements",
            ["link_start"],
            ["id"],
            ondelete="CASCADE",
        )
        batch.create_foreign_key(
            "links_link_destination_fkey",
            "requirements",
            ["link_destination"],
            ["id"],
            ondelete="CASCADE",
        )
        batch.drop_column("link_destination_kind")
        batch.drop_column("link_start_kind")
