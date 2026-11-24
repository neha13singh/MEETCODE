"""add points and point awards

Revision ID: a1b2c3d4e5f6
Revises: 0d3fa0005f34
Create Date: 2026-11-25

Adds the materialized ``users.points`` total and the idempotent
``point_awards`` ledger (50 per match win, 5 per first practice solve).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "0d3fa0005f34"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    if "users" in tables:
        columns = {column["name"] for column in inspector.get_columns("users")}
        if "points" not in columns:
            op.add_column(
                "users",
                sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
            )

    if "point_awards" not in tables:
        op.create_table(
            "point_awards",
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column("user_id", sa.UUID(), nullable=False),
            sa.Column("amount", sa.Integer(), nullable=False),
            sa.Column("reason", sa.String(length=30), nullable=False),
            sa.Column("reference_id", sa.UUID(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "user_id", "reason", "reference_id",
                name="uq_point_award_user_reason_reference",
            ),
        )
        op.create_index(
            op.f("ix_point_awards_user_id"), "point_awards", ["user_id"], unique=False
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    if "point_awards" in tables:
        op.drop_index(op.f("ix_point_awards_user_id"), table_name="point_awards")
        op.drop_table("point_awards")

    if "users" in tables:
        columns = {column["name"] for column in inspector.get_columns("users")}
        if "points" in columns:
            op.drop_column("users", "points")
