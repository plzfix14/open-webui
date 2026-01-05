"""Add password_reset_token table

Revision ID: e4c4c9e8f2a1
Revises: c440947495f3
Create Date: 2026-01-05 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e4c4c9e8f2a1"
down_revision: Union[str, None] = "c440947495f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "password_reset_token",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.BigInteger(), nullable=False),
        sa.Column("used", sa.Boolean(), default=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        # indexes
        sa.Index("ix_password_reset_token_user_id", "user_id"),
        sa.Index("ix_password_reset_token_token_hash", "token_hash"),
        sa.Index("ix_password_reset_token_expires_at", "expires_at"),
    )


def downgrade() -> None:
    op.drop_table("password_reset_token")
