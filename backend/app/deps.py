from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.repositories import usuario_repo
from app.security import decodificar_token

_bearer = HTTPBearer(auto_error=False)

DbSessao = Annotated[Session, Depends(get_db)]


def _nao_autenticado() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão expirada. Entre novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def usuario_atual(
    db: DbSessao,
    credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> Usuario:
    if credenciais is None:
        raise _nao_autenticado()
    try:
        payload = decodificar_token(credenciais.credentials)
        usuario = usuario_repo.por_id(db, int(payload["sub"]))
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise _nao_autenticado() from None
    # Token de antes do logout (versão antiga) ou de usuário desativado não vale.
    if usuario is None or not usuario.ativo or payload.get("ver") != usuario.versao_token:
        raise _nao_autenticado()
    return usuario


def exigir_administrador(usuario: Annotated[Usuario, Depends(usuario_atual)]) -> Usuario:
    if usuario.perfil != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta função é exclusiva da coordenação.",
        )
    return usuario


UsuarioAtual = Annotated[Usuario, Depends(usuario_atual)]
Administrador = Annotated[Usuario, Depends(exigir_administrador)]
