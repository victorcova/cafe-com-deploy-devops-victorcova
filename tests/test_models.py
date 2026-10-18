"""Teste isolado de persistência do modelo em banco temporário."""

from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models import Base, Cafe


def test_persiste_cafe_com_preco_decimal():
    # SQLite em memória mantém este teste isolado de qualquer banco real.
    motor = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(motor)
    with Session(motor) as sessao:
        sessao.add(Cafe(nome="Café de teste", preco=Decimal("12.50")))
        sessao.commit()
        cafe = sessao.scalar(select(Cafe).where(Cafe.nome == "Café de teste"))
        assert cafe is not None
        assert cafe.preco == Decimal("12.50")
    motor.dispose()