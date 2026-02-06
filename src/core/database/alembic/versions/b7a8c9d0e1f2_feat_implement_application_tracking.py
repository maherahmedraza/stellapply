"""feat: implement application tracking

Revision ID: b7a8c9d0e1f2
Revises: f3829d76fdbf
Create Date: 2026-02-05 23:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b7a8c9d0e1f2"
down_revision: Union[str, Sequence[str], None] = ["f3829d76fdbf", "b24b82412995"]
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create applicationstatus enum
    op.execute(
        "CREATE TYPE applicationstatus AS ENUM ('wishlist', 'applied', 'screening', 'interview', 'offer', 'rejected', 'accepted', 'withdrawn')"
    )

    # Create applications table
    op.create_table(
        "applications",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("job_id", sa.UUID(), nullable=True),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("job_title", sa.String(length=255), nullable=False),
        sa.Column("job_url", sa.String(length=1024), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "wishlist",
                "applied",
                "screening",
                "interview",
                "offer",
                "rejected",
                "accepted",
                "withdrawn",
                name="applicationstatus",
            ),
            nullable=False,
            server_default="wishlist",
        ),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("salary_min", sa.Integer(), nullable=True),
        sa.Column("salary_max", sa.Integer(), nullable=True),
        sa.Column(
            "salary_currency", sa.String(length=3), nullable=False, server_default="EUR"
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("resume_id", sa.UUID(), nullable=True),
        sa.Column("cover_letter_id", sa.UUID(), nullable=True),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("excitement_rating", sa.Integer(), nullable=True),
        sa.Column("next_follow_up", sa.DateTime(timezone=True), nullable=True),
        # BaseModel columns
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"]),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(
        op.f("ix_applications_user_id"), "applications", ["user_id"], unique=False
    )
    op.create_index(
        "ix_applications_user_status",
        "applications",
        ["user_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_applications_user_next_follow_up",
        "applications",
        ["user_id", "next_follow_up"],
        unique=False,
    )
    op.create_index(
        "ix_applications_user_created_at_desc",
        "applications",
        ["user_id", "created_at"],
        unique=False,
        postgresql_using="btree",
        postgresql_ops={"created_at": "desc"},
    )

    # Create application_events table
    op.create_table(
        "application_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("application_id", sa.UUID(), nullable=False),
        sa.Column("from_status", sa.String(length=50), nullable=True),
        sa.Column("to_status", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=False),
        # BaseModel columns
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["application_id"], ["applications.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_application_events_application_id"),
        "application_events",
        ["application_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_application_events_application_id"), table_name="application_events"
    )
    op.drop_table("application_events")

    op.drop_index("ix_applications_user_created_at_desc", table_name="applications")
    op.drop_index("ix_applications_user_next_follow_up", table_name="applications")
    op.drop_index("ix_applications_user_status", table_name="applications")
    op.drop_index(op.f("ix_applications_user_id"), table_name="applications")
    op.drop_table("applications")

    op.execute("DROP TYPE applicationstatus")
