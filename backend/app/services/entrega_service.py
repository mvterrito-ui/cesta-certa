from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Entrega, Usuario
from app.repositories import entrega_repo, familia_repo
from app.schemas import EntregaRegistrada
from app.services.erros import Conflito, NaoEncontrado
from app.services.regras_entrega import mensagem_bloqueio, pode_receber, proxima_entrega
from app.tempo import agora_utc, data_local


def registrar(
    db: Session, familia_id: int, usuario: Usuario, observacao: str | None = None
) -> EntregaRegistrada:
    """Registra a entrega (RF02) se a família estiver apta pela regra dos 15 dias (RF03)."""
    intervalo = get_settings().intervalo_entrega_dias
    familia = familia_repo.por_id(db, familia_id, bloquear=True)
    if familia is None:
        raise NaoEncontrado("Família não encontrada.")
    if familia.status != "ativa":
        raise Conflito("Esta família está inativa. Fale com a coordenação.")

    agora = agora_utc()
    hoje = data_local(agora)
    ultima = entrega_repo.ultima(db, familia_id)
    if ultima is not None:
        ultima_dia = data_local(ultima.data_entrega)
        if not pode_receber(ultima_dia, hoje, intervalo):
            # Nome de quem entregou: a coordenação sabe a quem perguntar quando
            # a família contesta o bloqueio (feedback da 1ª rodada de validação).
            entregue_por = ultima.usuario.nome
            db.rollback()
            raise Conflito(
                mensagem_bloqueio(ultima_dia, intervalo),
                ultima_entrega=ultima_dia.isoformat(),
                proxima_entrega=proxima_entrega(ultima_dia, intervalo).isoformat(),
                entregue_por=entregue_por,
            )

    entrega = entrega_repo.criar(
        db,
        Entrega(
            familia_id=familia.id,
            usuario_id=usuario.id,
            data_entrega=agora,
            observacao=observacao,
        ),
    )
    db.commit()
    return EntregaRegistrada(
        id=entrega.id,
        familia_id=familia.id,
        nome_responsavel=familia.nome_responsavel,
        data_entrega=agora,
        proxima_entrega=proxima_entrega(hoje, intervalo),
    )
