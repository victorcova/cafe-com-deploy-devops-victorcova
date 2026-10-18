"""Conexão com o banco, configurada por variável de ambiente."""

import os
from functools import lru_cache
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


@lru_cache(maxsize=1)
def obter_motor() -> Engine:
    """Cria a conexão somente quando uma rota de catálogo precisar dela."""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("Configure DATABASE_URL para acessar o catálogo")
    return create_engine(url, pool_pre_ping=True)


def obter_sessao() -> Iterator[Session]:
    """Fornece uma sessão por requisição e a encerra ao final."""
    with Session(obter_motor()) as sessao:
        yield sessao
