from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.cpf import cpf_valido, somente_digitos


class LoginEntrada(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1, max_length=128)


class UsuarioSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str
    perfil: str


class TokenSaida(BaseModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105
    usuario: UsuarioSaida


class UsuarioEntrada(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    perfil: Literal["administrador", "voluntario"] = "voluntario"


class FamiliaEntrada(BaseModel):
    nome_responsavel: str = Field(min_length=3, max_length=120)
    documento_responsavel: str
    telefone: str | None = Field(default=None, max_length=15)
    endereco: str = Field(min_length=3, max_length=200)
    numero_integrantes: int = Field(gt=0, le=30)
    observacao: str | None = Field(default=None, max_length=300)

    @field_validator("nome_responsavel", "endereco")
    @classmethod
    def remover_espacos(cls, valor: str) -> str:
        return " ".join(valor.split())

    @field_validator("documento_responsavel")
    @classmethod
    def validar_cpf(cls, valor: str) -> str:
        if not cpf_valido(valor):
            raise ValueError("CPF inválido. Confira os 11 números.")
        return somente_digitos(valor)


class FamiliaResumo(BaseModel):
    id: int
    nome_responsavel: str
    numero_integrantes: int
    cpf: str
    ultima_entrega: date | None
    apta: bool
    proxima_entrega: date | None


class EntregaSaida(BaseModel):
    id: int
    data_entrega: datetime
    registrado_por: str


class FamiliaDetalhe(FamiliaResumo):
    endereco: str
    telefone: str | None
    observacao: str | None
    status: str
    entregas: list[EntregaSaida]


class EntregaEntrada(BaseModel):
    observacao: str | None = Field(default=None, max_length=300)


class EntregaRegistrada(BaseModel):
    id: int
    familia_id: int
    nome_responsavel: str
    data_entrega: datetime
    proxima_entrega: date


class EntregasPorVoluntario(BaseModel):
    nome: str
    entregas: int


class RelatorioMensal(BaseModel):
    ano: int
    mes: int
    total_entregas: int
    familias_atendidas: int
    pessoas_atendidas: int
    familias_ativas: int
    familias_sem_entrega: int
    por_voluntario: list[EntregasPorVoluntario]
