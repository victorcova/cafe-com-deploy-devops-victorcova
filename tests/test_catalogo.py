"""Testes HTTP do catálogo com banco temporário isolado."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import obter_sessao
from app.main import app
from app.models import Base


@pytest.fixture
def cliente_catalogo():
    motor = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(motor)

    def sessao_de_teste():
        with Session(motor) as sessao:
            yield sessao

    app.dependency_overrides[obter_sessao] = sessao_de_teste
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()
    motor.dispose()


def test_cadastra_lista_e_consulta_cafe(cliente_catalogo):
    resposta = cliente_catalogo.post("/cafes", json={"nome": "Café de teste", "preco": "12.50"})
    assert resposta.status_code == 201
    cafe = resposta.json()
    assert cafe["nome"] == "Café de teste"
    assert cafe["preco"] == "12.50"
    assert cliente_catalogo.get("/cafes").json() == [cafe]
    assert cliente_catalogo.get(f"/cafes/{cafe['id']}").json() == cafe


def test_calcula_preco_e_rejeita_desconto_acima_do_limite(cliente_catalogo, monkeypatch):
    monkeypatch.setenv("DESCONTO_MAXIMO", "50")
    cafe = cliente_catalogo.post("/cafes", json={"nome": "Café A", "preco": "10.00"}).json()
    caminho = f"/cafes/{cafe['id']}/preco"
    assert cliente_catalogo.get(caminho, params={"desconto": 10}).json()["preco_final"] == 9.0
    assert cliente_catalogo.get(caminho, params={"desconto": 80}).status_code == 422


def test_rejeita_nome_duplicado(cliente_catalogo):
    dados = {"nome": "Café único", "preco": "10.00"}
    assert cliente_catalogo.post("/cafes", json=dados).status_code == 201
    assert cliente_catalogo.post("/cafes", json=dados).status_code == 409


def test_rejeita_preco_negativo_e_nome_em_branco(cliente_catalogo):
    assert cliente_catalogo.post("/cafes", json={"nome": "Café", "preco": "-1"}).status_code == 422
    assert cliente_catalogo.post("/cafes", json={"nome": "   ", "preco": "10"}).status_code == 422


def test_retorna_404_para_cafe_inexistente(cliente_catalogo):
    assert cliente_catalogo.get("/cafes/999").status_code == 404
    assert cliente_catalogo.get("/cafes/999/preco").status_code == 404
