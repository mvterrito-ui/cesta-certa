from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(tags=["saúde"])


@router.api_route("/saude", methods=["GET", "HEAD"])
def saude():
    """Verificação de saúde da API, sem tocar no banco.

    Consultada pelo UptimeRobot (que usa HEAD) a cada 5 minutos para o Render
    não hibernar a API. Não consulta o banco de propósito: o Neon só suspende o
    compute após 5 minutos sem atividade, e um "SELECT 1" nesse ritmo o
    manteria ligado 24h, esgotando as horas de compute do plano gratuito.
    """
    return {"status": "ok"}


@router.api_route("/saude/banco", methods=["GET", "HEAD"])
def saude_banco(db: Annotated[Session, Depends(get_db)]):
    """Verificação de saúde que também consulta o banco.

    Use com pouca frequência (ex.: rotina diária do GitHub Actions), nunca em
    monitoramento a cada poucos minutos.
    """
    db.execute(text("SELECT 1"))
    return {"status": "ok", "banco": "ok"}
