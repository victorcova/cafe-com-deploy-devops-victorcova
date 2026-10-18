"""Insere cinco cafés de exemplo.

Revision ID: 002
Revises: 001
"""

from decimal import Decimal

from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None

cafes = sa.table(
    "cafes",
    sa.column("nome", sa.String),
    sa.column("preco", sa.Numeric),
)


def upgrade() -> None:
    op.bulk_insert(cafes, [
        {"nome": "Café do Cerrado", "preco": Decimal("12.00")},
        {"nome": "Café da Mantiqueira", "preco": Decimal("14.50")},
        {"nome": "Café da Chapada", "preco": Decimal("13.00")},
        {"nome": "Café da Mogiana", "preco": Decimal("11.50")},
        {"nome": "Café Sul de Minas", "preco": Decimal("10.00")},
    ])


def downgrade() -> None:
    # Remove apenas os itens de exemplo; outras alterações exigem análise prévia.
    op.execute(cafes.delete().where(cafes.c.nome.in_([
        "Café do Cerrado", "Café da Mantiqueira", "Café da Chapada",
        "Café da Mogiana", "Café Sul de Minas",
    ])))
