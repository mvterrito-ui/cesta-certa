from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.cpf import formatar_cpf, mascarar_cpf, somente_digitos
from app.models import Familia, Usuario
from app.repositories import entrega_repo, familia_repo
from app.schemas import EntregaSaida, FamiliaDetalhe, FamiliaEntrada, FamiliaResumo
from app.services.erros import Conflito, ErroDeNegocio, NaoEncontrado
from app.services.regras_entrega import pode_receber, proxima_entrega
from app.tempo import data_local, hoje_local

MENSAGEM_CPF_DUPLICADO = "Já existe uma família cadastrada com este CPF."


def cpf_para_exibir(documento: str, usuario: Usuario) -> str:
    # Voluntário vê só os dígitos centrais; o administrador vê o CPF completo (RNF02).
    if usuario.perfil == "administrador":
        return formatar_cpf(documento)
    return mascarar_cpf(documento)


def _resumo(familia: Familia, ultima, usuario: Usuario) -> dict:
    intervalo = get_settings().intervalo_entrega_dias
    ultima_dia = data_local(ultima) if ultima else None
    return {
        "id": familia.id,
        "nome_responsavel": familia.nome_responsavel,
        "numero_integrantes": familia.numero_integrantes,
        "cpf": cpf_para_exibir(familia.documento_responsavel, usuario),
        "ultima_entrega": ultima_dia,
        "apta": pode_receber(ultima_dia, hoje_local(), intervalo),
        "proxima_entrega": proxima_entrega(ultima_dia, intervalo) if ultima_dia else None,
    }


def buscar(db: Session, termo: str, usuario: Usuario) -> list[FamiliaResumo]:
    termo = " ".join(termo.split())
    digitos = somente_digitos(termo)
    if len(digitos) == 11 and not any(c.isalpha() for c in termo):
        termo = digitos
    elif len(termo) < 3 or termo.isdigit():
        raise ErroDeNegocio("Digite pelo menos 3 letras ou o CPF completo.", status=422)

    familias = familia_repo.buscar_ativas(db, termo)
    ultimas = entrega_repo.ultimas_datas(db, [f.id for f in familias])
    return [FamiliaResumo(**_resumo(f, ultimas.get(f.id), usuario)) for f in familias]


def detalhar(db: Session, familia_id: int, usuario: Usuario) -> FamiliaDetalhe:
    familia = familia_repo.por_id(db, familia_id)
    if familia is None:
        raise NaoEncontrado("Família não encontrada.")
    historico = entrega_repo.historico(db, familia_id)
    ultima = historico[0].data_entrega if historico else None
    return FamiliaDetalhe(
        **_resumo(familia, ultima, usuario),
        endereco=familia.endereco,
        telefone=familia.telefone,
        observacao=familia.observacao,
        status=familia.status,
        entregas=[
            EntregaSaida(id=e.id, data_entrega=e.data_entrega, registrado_por=e.usuario.nome)
            for e in historico
        ],
    )


def cadastrar(db: Session, dados: FamiliaEntrada, usuario: Usuario) -> FamiliaDetalhe:
    if familia_repo.por_documento(db, dados.documento_responsavel):
        raise Conflito(MENSAGEM_CPF_DUPLICADO)
    try:
        familia = familia_repo.criar(db, Familia(**dados.model_dump(), cadastrado_por=usuario.id))
        db.commit()
    except IntegrityError:
        # Dois cadastros simultâneos do mesmo CPF: a restrição UNIQUE decide.
        db.rollback()
        raise Conflito(MENSAGEM_CPF_DUPLICADO) from None
    return detalhar(db, familia.id, usuario)
