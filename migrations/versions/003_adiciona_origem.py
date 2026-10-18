"""Adiciona origem aos cafes sem alterar o catalogo existente.

Revision ID: 003
Revises: 002
"""

from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "cafes",
        sa.Column("origem", sa.String(100), nullable=False, server_default="Nao informada"),
    )


def downgrade() -> None:
    # Remove a coluna e seus valores; nao executar se precisar preserva-los.
    op.drop_column("cafes", "origem")
