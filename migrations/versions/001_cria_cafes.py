"""Cria a tabela de cafés.

Revision ID: 001
Revises: None
"""

from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cafes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(80), nullable=False, unique=True),
        sa.Column("preco", sa.Numeric(6, 2), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("cafes")
