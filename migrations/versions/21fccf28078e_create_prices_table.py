"""create prices table

Revision ID: 21fccf28078e
Revises:
Create Date: 2026-10-14 11:24:27.253173

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "21fccf28078e"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "prices",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("ticker", sa.String(length=16), nullable=False),
        sa.Column("price", sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_prices_ticker_timestamp", "prices", ["ticker", "timestamp"])


def downgrade() -> None:
    op.drop_index("ix_prices_ticker_timestamp", table_name="prices")
    op.drop_table("prices")
