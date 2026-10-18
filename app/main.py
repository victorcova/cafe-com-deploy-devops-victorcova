"""API e regra inicial de preços da Café com Deploy."""

import os
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import obter_sessao
from app.models import Cafe

app = FastAPI(title="Café com Deploy")


def preco_com_desconto(preco: float, pct: float) -> float:
    """Calcula o preço em centavos respeitando o limite de desconto configurado."""
    try:
        valor = Decimal(str(preco))
        desconto = Decimal(str(pct))
        maximo = Decimal(os.getenv("DESCONTO_MAXIMO", "50"))
    except InvalidOperation as erro:
        raise ValueError("Preço ou desconto inválido") from erro

    if not all(numero.is_finite() for numero in (valor, desconto, maximo)):
        raise ValueError("Preço e descontos devem ser valores finitos")
    if valor < 0 or not Decimal("0") <= maximo <= Decimal("100"):
        raise ValueError("Preço ou limite de desconto inválido")
    if not Decimal("0") <= desconto <= maximo:
        raise ValueError("Desconto fora do limite permitido")

    resultado = valor * (Decimal("1") - desconto / Decimal("10"))
    return float(resultado.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


@app.get("/health")
def health() -> dict[str, str]:
    """Informa se a aplicação responde; não verifica o banco de dados."""
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    """Identifica a versão configurada para a aplicação."""
    return {"version": os.getenv("APP_VERSION", "dev")}


class CafeEntrada(BaseModel):
    """Dados necessários para cadastrar um café."""

    nome: str = Field(min_length=1, max_length=80)
    preco: Decimal = Field(gt=0, max_digits=6, decimal_places=2)

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, nome: str) -> str:
        nome = nome.strip()
        if not nome:
            raise ValueError("O nome não pode ficar em branco")
        return nome


class CafeResposta(CafeEntrada):
    """Representação do café retornada ao cliente."""

    model_config = ConfigDict(from_attributes=True)
    id: int


@app.get("/cafes", response_model=list[CafeResposta])
def listar_cafes(sessao: Session = Depends(obter_sessao)) -> list[Cafe]:
    """Lista o catálogo ordenado pelo identificador."""
    return list(sessao.scalars(select(Cafe).order_by(Cafe.id)))


@app.post("/cafes", response_model=CafeResposta, status_code=status.HTTP_201_CREATED)
def cadastrar_cafe(dados: CafeEntrada, sessao: Session = Depends(obter_sessao)) -> Cafe:
    """Cadastra um café com nome único e preço positivo."""
    cafe = Cafe(nome=dados.nome, preco=dados.preco)
    sessao.add(cafe)
    try:
        sessao.commit()
    except IntegrityError as erro:
        sessao.rollback()
        raise HTTPException(status_code=409, detail="Já existe um café com esse nome") from erro
    sessao.refresh(cafe)
    return cafe


def buscar_cafe_por_id(identificador: int, sessao: Session) -> Cafe:
    cafe = sessao.get(Cafe, identificador)
    if cafe is None:
        raise HTTPException(status_code=404, detail="Café não encontrado")
    return cafe


@app.get("/cafes/{id}", response_model=CafeResposta)
def obter_cafe(id: int, sessao: Session = Depends(obter_sessao)) -> Cafe:
    """Consulta um café pelo identificador."""
    return buscar_cafe_por_id(id, sessao)


@app.get("/cafes/{id}/preco")
def consultar_preco(
    id: int,
    desconto: float = Query(default=0, ge=0, le=100),
    sessao: Session = Depends(obter_sessao),
) -> dict[str, float | int]:
    """Calcula o preço do café com o desconto solicitado."""
    cafe = buscar_cafe_por_id(id, sessao)
    try:
        preco_final = preco_com_desconto(float(cafe.preco), desconto)
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro
    return {"id": cafe.id, "desconto": desconto, "preco_final": preco_final}
