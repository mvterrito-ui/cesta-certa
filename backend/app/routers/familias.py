from typing import Annotated

from fastapi import APIRouter, Query, status

from app.deps import DbSessao, UsuarioAtual
from app.schemas import (
    EntregaEntrada,
    EntregaRegistrada,
    FamiliaDetalhe,
    FamiliaEntrada,
    FamiliaResumo,
)
from app.services import entrega_service, familia_service

router = APIRouter(prefix="/familias", tags=["famílias e entregas"])


@router.get("", response_model=list[FamiliaResumo])
def buscar(
    usuario: UsuarioAtual,
    db: DbSessao,
    busca: Annotated[str, Query(max_length=120)] = "",
):
    """Tela 1: busca por parte do nome ou CPF completo."""
    return familia_service.buscar(db, busca, usuario)


@router.post("", response_model=FamiliaDetalhe, status_code=status.HTTP_201_CREATED)
def cadastrar(dados: FamiliaEntrada, usuario: UsuarioAtual, db: DbSessao):
    """RF01: cadastro de família com CPF único."""
    return familia_service.cadastrar(db, dados, usuario)


@router.get("/{familia_id}", response_model=FamiliaDetalhe)
def detalhar(familia_id: int, usuario: UsuarioAtual, db: DbSessao):
    """Tela 2: dados da família e últimas entregas."""
    return familia_service.detalhar(db, familia_id, usuario)


@router.post(
    "/{familia_id}/entregas",
    response_model=EntregaRegistrada,
    status_code=status.HTTP_201_CREATED,
)
def registrar_entrega(
    familia_id: int,
    usuario: UsuarioAtual,
    db: DbSessao,
    dados: EntregaEntrada | None = None,
):
    """RF02 e RF03: registra a entrega ou devolve 409 se ainda não passaram 15 dias."""
    observacao = dados.observacao if dados else None
    return entrega_service.registrar(db, familia_id, usuario, observacao)
