"""Configuração do Alembic com URL fornecida pelo ambiente."""

import os

from alembic import context
from sqlalchemy import create_engine, pool

from app.models import Base

config = context.config
target_metadata = Base.metadata
url_banco = os.environ.get("DATABASE_URL")
if not url_banco:
    raise RuntimeError("Defina DATABASE_URL antes de executar as migrations")


def executar_offline() -> None:
    context.configure(url=url_banco, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def executar_online() -> None:
    conexao = create_engine(url_banco, poolclass=pool.NullPool)
    with conexao.connect() as conexao_banco:
        context.configure(connection=conexao_banco, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    conexao.dispose()


if context.is_offline_mode():
    executar_offline()
else:
    executar_online()
