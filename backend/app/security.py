from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.config import get_settings


def gerar_hash_senha(senha: str) -> str:
    rounds = get_settings().bcrypt_rounds
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt(rounds=rounds)).decode()


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode(), senha_hash.encode())


def criar_token(usuario_id: int, perfil: str, versao_token: int) -> str:
    settings = get_settings()
    agora = datetime.now(UTC)
    payload = {
        "sub": str(usuario_id),
        "perfil": perfil,
        "ver": versao_token,
        "iat": agora,
        "exp": agora + timedelta(hours=settings.jwt_expiracao_horas),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algoritmo)


def decodificar_token(token: str) -> dict:
    """Lança jwt.InvalidTokenError se o token for inválido ou expirado."""
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algoritmo])
