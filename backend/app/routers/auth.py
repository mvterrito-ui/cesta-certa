from fastapi import APIRouter, status

from app.deps import Administrador, DbSessao, UsuarioAtual
from app.schemas import LoginEntrada, TokenSaida, UsuarioEntrada, UsuarioSaida
from app.services import auth_service

router = APIRouter(tags=["autenticação"])


@router.post("/auth/login", response_model=TokenSaida)
def login(dados: LoginEntrada, db: DbSessao):
    token, usuario = auth_service.login(db, dados.email, dados.senha)
    return TokenSaida(access_token=token, usuario=UsuarioSaida.model_validate(usuario))


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(usuario: UsuarioAtual, db: DbSessao):
    auth_service.logout(db, usuario)


@router.get("/auth/me", response_model=UsuarioSaida)
def eu(usuario: UsuarioAtual):
    return usuario


@router.post("/usuarios", response_model=UsuarioSaida, status_code=status.HTTP_201_CREATED)
def criar_usuario(dados: UsuarioEntrada, _: Administrador, db: DbSessao):
    return auth_service.criar_usuario(db, dados.nome, dados.email, dados.senha, dados.perfil)
