from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Usuario


def por_email(db: Session, email: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.email == email.lower()))


def por_id(db: Session, usuario_id: int) -> Usuario | None:
    return db.get(Usuario, usuario_id)


def criar(db: Session, usuario: Usuario) -> Usuario:
    db.add(usuario)
    db.flush()
    return usuario
