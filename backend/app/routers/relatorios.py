from typing import Annotated

from fastapi import APIRouter, Query

from app.deps import Administrador, DbSessao
from app.schemas import RelatorioMensal
from app.services import relatorio_service

router = APIRouter(prefix="/relatorios", tags=["relatórios"])


@router.get("/mensal", response_model=RelatorioMensal)
def mensal(
    _: Administrador,
    db: DbSessao,
    ano: Annotated[int, Query(ge=2024, le=2100)],
    mes: Annotated[int, Query(ge=1, le=12)],
):
    """RF04: relatório mensal, exclusivo da coordenação."""
    return relatorio_service.mensal(db, ano, mes)
