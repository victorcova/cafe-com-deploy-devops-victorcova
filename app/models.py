"""Modelo da tabela de cafés."""

from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base dos modelos usados pelo SQLAlchemy e pelo Alembic."""


class Cafe(Base):
    """Café disponível no catálogo."""

    __tablename__ = "cafes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    preco: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
