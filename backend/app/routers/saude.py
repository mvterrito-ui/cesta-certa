from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(tags=["saúde"])


@router.api_route("/saude", methods=["GET", "HEAD"])
def saude(db: Annotated[Session, Depends(get_db)]):
    """Verificação de saúde da API e do banco.

    Consultada pelo UptimeRobot (que usa HEAD) a cada 5 minutos e pelo GitHub
    Actions; também evita que a API e o banco hibernem no plano gratuito.
    """
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
