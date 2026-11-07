from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Familia
from app.texto import normalizar_busca


def buscar_ativas(db: Session, termo: str, limite: int = 20) -> list[Familia]:
    consulta = select(Familia).where(Familia.status == "ativa")
    if termo.isdigit():
        consulta = consulta.where(Familia.documento_responsavel == termo)
    else:
        # Compara sem acentos e sem diferenciar maiúsculas: "antonio" acha "Antônio".
        # O termo vai como parâmetro da consulta, nunca concatenado no SQL (RNF02).
        termo = normalizar_busca(termo)
        termo = termo.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        consulta = consulta.where(Familia.nome_busca.like(f"%{termo}%", escape="\\"))
    return list(db.scalars(consulta.order_by(Familia.nome_responsavel).limit(limite)))


def por_id(db: Session, familia_id: int, bloquear: bool = False) -> Familia | None:
    consulta = select(Familia).where(Familia.id == familia_id)
    if bloquear:
        # Trava a linha da família até o fim da transação: dois voluntários
        # não conseguem registrar a mesma entrega ao mesmo tempo.
        consulta = consulta.with_for_update()
    return db.scalar(consulta)


def por_documento(db: Session, documento: str) -> Familia | None:
    return db.scalar(select(Familia).where(Familia.documento_responsavel == documento))


def criar(db: Session, familia: Familia) -> Familia:
    db.add(familia)
    db.flush()
    return familia
