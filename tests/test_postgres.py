"""Integração com banco PostgreSQL dedicado exclusivamente a testes."""

import os
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models import Cafe


@pytest.mark.skipif(
    not os.getenv("DATABASE_TEST_URL"),
    reason="DATABASE_TEST_URL não configurada para banco dedicado de teste",
)
def test_migrations_e_persistencia_no_postgresql():
    motor = create_engine(os.environ["DATABASE_TEST_URL"])
    try:
        with Session(motor) as sessao:
            # A transação é desfeita para não alterar o estado do banco de teste.
            assert sessao.scalar(select(Cafe).where(Cafe.nome == "Café do Cerrado")) is not None
            cafe = Cafe(nome="Café de integração temporário", preco=Decimal("19.90"))
            sessao.add(cafe)
            sessao.flush()
            identificador = cafe.id
            sessao.expire_all()
            assert sessao.get(Cafe, identificador).preco == Decimal("19.90")
            sessao.rollback()
    finally:
        motor.dispose()
