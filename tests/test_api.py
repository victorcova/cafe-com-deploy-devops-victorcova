"""Testes HTTP das rotas essenciais da API."""

from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)


def test_health_responde_com_sucesso():
    resposta = cliente.get("/health")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_version_informa_versao_configurada(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "abc1234")
    resposta = cliente.get("/version")
    assert resposta.status_code == 200
    assert resposta.json() == {"version": "abc1234"}


def test_version_usa_padrao_no_ambiente_local(monkeypatch):
    monkeypatch.delenv("APP_VERSION", raising=False)
    assert cliente.get("/version").json() == {"version": "dev"}
