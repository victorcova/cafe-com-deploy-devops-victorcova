# A etapa de dependências é separada da imagem usada para executar a API.
FROM python:3.14-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

FROM base AS dependencias
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --prefix=/instalacao -r requirements.txt

FROM base AS execucao
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}
COPY --from=dependencias /instalacao /usr/local
RUN useradd --create-home --uid 10001 appuser
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser migrations/ ./migrations/
COPY --chown=appuser:appuser alembic.ini ./
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8000') + '/health', timeout=3)"
# As migrations são aplicadas no banco configurado antes de iniciar a API.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
