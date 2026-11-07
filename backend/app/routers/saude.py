from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(tags=["saúde"])


@router.get("/saude")
def saude(db: Annotated[Session, Depends(get_db)]):
    """Consultado pelo GitHub Actions para manter a API e o Supabase ativos."""
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
