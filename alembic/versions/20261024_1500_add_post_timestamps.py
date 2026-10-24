"""Add created_at and updated_at to posts."""

import sqlalchemy as sa
from alembic import op

revision = "20261024_1500"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    if not inspector.has_table("posts"):
        raise RuntimeError(
            "The posts table does not exist. Start the application once to create "
            "the initial table, then run this migration again."
        )

    existing_columns = {column["name"] for column in inspector.get_columns("posts")}
    if "created_at" not in existing_columns:
        op.add_column(
            "posts",
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
        )
    if "updated_at" not in existing_columns:
        op.add_column(
            "posts",
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
        )


def downgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    if not inspector.has_table("posts"):
        return

    existing_columns = {column["name"] for column in inspector.get_columns("posts")}
    if "updated_at" in existing_columns:
        op.drop_column("posts", "updated_at")
    if "created_at" in existing_columns:
        op.drop_column("posts", "created_at")
