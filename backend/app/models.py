from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.tempo import agora_utc


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = (
        CheckConstraint("perfil IN ('administrador', 'voluntario')", name="ck_usuario_perfil"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(100))
    perfil: Mapped[str] = mapped_column(String(20))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    # Incrementado no logout: tokens emitidos antes deixam de valer (RNF01).
    versao_token: Mapped[int] = mapped_column(Integer, default=0)
    tentativas_falhas: Mapped[int] = mapped_column(Integer, default=0)
    bloqueado_ate: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc)


class Familia(Base):
    __tablename__ = "familia"
    __table_args__ = (
        CheckConstraint("numero_integrantes > 0", name="ck_familia_integrantes"),
        CheckConstraint("status IN ('ativa', 'inativa')", name="ck_familia_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome_responsavel: Mapped[str] = mapped_column(String(120), index=True)
    # CPF só com dígitos; UNIQUE impede cadastrar a mesma família duas vezes (RF01).
    documento_responsavel: Mapped[str] = mapped_column(String(11), unique=True)
    telefone: Mapped[str | None] = mapped_column(String(15))
    endereco: Mapped[str] = mapped_column(String(200))
    numero_integrantes: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(10), default="ativa")
    observacao: Mapped[str | None] = mapped_column(String(300))
    cadastrado_por: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=agora_utc, onupdate=agora_utc
    )

    entregas: Mapped[list["Entrega"]] = relationship(
        back_populates="familia", order_by="desc(Entrega.data_entrega)"
    )


class Entrega(Base):
    __tablename__ = "entrega"
    __table_args__ = (Index("ix_entrega_familia_data", "familia_id", "data_entrega"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    familia_id: Mapped[int] = mapped_column(ForeignKey("familia.id"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    # Definida pelo servidor, nunca pelo celular.
    data_entrega: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc)
    observacao: Mapped[str | None] = mapped_column(String(300))

    familia: Mapped[Familia] = relationship(back_populates="entregas")
    usuario: Mapped[Usuario] = relationship()
