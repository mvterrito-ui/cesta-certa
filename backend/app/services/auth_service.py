from datetime import timedelta

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Usuario
from app.repositories import usuario_repo
from app.security import criar_token, gerar_hash_senha, verificar_senha
from app.services.erros import Conflito, ErroDeNegocio
from app.tempo import agora_utc, como_utc

# Mensagem única para e-mail inexistente, senha errada ou usuário inativo,
# para não revelar quais e-mails estão cadastrados (RNF01).
MENSAGEM_LOGIN_INVALIDO = "E-mail ou senha inválidos."
MENSAGEM_BLOQUEIO = "Muitas tentativas seguidas. Aguarde 15 minutos e tente novamente."

# Hash usado quando o e-mail não existe, para o tempo de resposta ser parecido.
_HASH_FICTICIO = gerar_hash_senha("senha-inexistente")


def login(db: Session, email: str, senha: str) -> tuple[str, Usuario]:
    settings = get_settings()
    usuario = usuario_repo.por_email(db, email)
    agora = agora_utc()

    if usuario is None:
        verificar_senha(senha, _HASH_FICTICIO)
        raise ErroDeNegocio(MENSAGEM_LOGIN_INVALIDO, status=401)

    if usuario.bloqueado_ate and como_utc(usuario.bloqueado_ate) > agora:
        raise ErroDeNegocio(MENSAGEM_BLOQUEIO, status=429)

    if not verificar_senha(senha, usuario.senha_hash) or not usuario.ativo:
        usuario.tentativas_falhas += 1
        if usuario.tentativas_falhas >= settings.max_tentativas_login:
            usuario.bloqueado_ate = agora + timedelta(minutes=settings.bloqueio_minutos)
            usuario.tentativas_falhas = 0
        db.commit()
        raise ErroDeNegocio(MENSAGEM_LOGIN_INVALIDO, status=401)

    usuario.tentativas_falhas = 0
    usuario.bloqueado_ate = None
    db.commit()
    return criar_token(usuario.id, usuario.perfil, usuario.versao_token), usuario


def logout(db: Session, usuario: Usuario) -> None:
    usuario.versao_token += 1
    db.commit()


def criar_usuario(db: Session, nome: str, email: str, senha: str, perfil: str) -> Usuario:
    if usuario_repo.por_email(db, email):
        raise Conflito("Já existe um usuário com este e-mail.")
    usuario = usuario_repo.criar(
        db,
        Usuario(
            nome=nome,
            email=email.lower(),
            senha_hash=gerar_hash_senha(senha),
            perfil=perfil,
        ),
    )
    db.commit()
    return usuario
