from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Entrega


def ultimas_datas(db: Session, familia_ids: list[int]) -> dict[int, datetime]:
    """Data da entrega mais recente de cada família, em uma única consulta."""
    if not familia_ids:
        return {}
    consulta = (
        select(Entrega.familia_id, func.max(Entrega.data_entrega))
        .where(Entrega.familia_id.in_(familia_ids))
        .group_by(Entrega.familia_id)
    )
    return {familia_id: data for familia_id, data in db.execute(consulta)}


def ultima(db: Session, familia_id: int) -> Entrega | None:
    """Entrega mais recente da família, já com o voluntário que a registrou."""
    recentes = historico(db, familia_id, limite=1)
    return recentes[0] if recentes else None


def historico(db: Session, familia_id: int, limite: int = 5) -> list[Entrega]:
    consulta = (
        select(Entrega)
        .options(joinedload(Entrega.usuario))
        .where(Entrega.familia_id == familia_id)
        .order_by(Entrega.data_entrega.desc())
        .limit(limite)
    )
    return list(db.scalars(consulta))


def criar(db: Session, entrega: Entrega) -> Entrega:
    db.add(entrega)
    db.flush()
    return entrega
