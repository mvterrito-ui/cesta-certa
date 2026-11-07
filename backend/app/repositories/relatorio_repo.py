from datetime import datetime

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.models import Entrega, Familia, Usuario


def _no_periodo(inicio: datetime, fim: datetime):
    return Entrega.data_entrega >= inicio, Entrega.data_entrega < fim


def total_entregas(db: Session, inicio: datetime, fim: datetime) -> int:
    return db.scalar(select(func.count(Entrega.id)).where(*_no_periodo(inicio, fim))) or 0


def familias_atendidas(db: Session, inicio: datetime, fim: datetime) -> tuple[int, int]:
    """Quantidade de famílias atendidas e soma das pessoas dessas famílias."""
    atendidas = (
        select(distinct(Entrega.familia_id).label("familia_id"))
        .where(*_no_periodo(inicio, fim))
        .subquery()
    )
    pessoas = func.coalesce(func.sum(Familia.numero_integrantes), 0)
    consulta = select(func.count(Familia.id), pessoas).join(
        atendidas, atendidas.c.familia_id == Familia.id
    )
    familias, total_pessoas = db.execute(consulta).one()
    return familias, total_pessoas


def familias_ativas_sem_entrega(db: Session, inicio: datetime, fim: datetime) -> tuple[int, int]:
    """Total de famílias ativas e quantas delas não receberam cesta no período."""
    atendidas = select(Entrega.familia_id).where(*_no_periodo(inicio, fim))
    ativas = db.scalar(select(func.count(Familia.id)).where(Familia.status == "ativa")) or 0
    sem_entrega = (
        db.scalar(
            select(func.count(Familia.id)).where(
                Familia.status == "ativa", Familia.id.not_in(atendidas)
            )
        )
        or 0
    )
    return ativas, sem_entrega


def entregas_por_voluntario(db: Session, inicio: datetime, fim: datetime) -> list[tuple[str, int]]:
    consulta = (
        select(Usuario.nome, func.count(Entrega.id).label("total"))
        .join(Entrega, Entrega.usuario_id == Usuario.id)
        .where(*_no_periodo(inicio, fim))
        .group_by(Usuario.id, Usuario.nome)
        .order_by(func.count(Entrega.id).desc(), Usuario.nome)
    )
    return [(nome, total) for nome, total in db.execute(consulta)]
