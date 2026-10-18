"""Testes da regra de desconto, sem acesso a serviços externos."""

import pytest

from app.main import preco_com_desconto


@pytest.mark.parametrize(
    ("preco", "desconto", "esperado"),
    [(10.0, 0, 10.0), (10.0, 10, 9.0), (8.5, 50, 4.25), (1.05, 50, 0.53)],
)
def test_calcula_descontos_validos(preco, desconto, esperado, monkeypatch):
    monkeypatch.setenv("DESCONTO_MAXIMO", "50")
    assert preco_com_desconto(preco, desconto) == esperado


@pytest.mark.parametrize("desconto", [-1, 51, 80])
def test_rejeita_desconto_fora_do_limite(desconto, monkeypatch):
    monkeypatch.setenv("DESCONTO_MAXIMO", "50")
    with pytest.raises(ValueError, match="Desconto fora"):
        preco_com_desconto(10, desconto)


def test_respeita_limite_configurado(monkeypatch):
    monkeypatch.setenv("DESCONTO_MAXIMO", "20")
    with pytest.raises(ValueError, match="Desconto fora"):
        preco_com_desconto(10, 21)


def test_rejeita_preco_negativo(monkeypatch):
    monkeypatch.setenv("DESCONTO_MAXIMO", "50")
    with pytest.raises(ValueError, match="Preço ou limite"):
        preco_com_desconto(-1, 10)
