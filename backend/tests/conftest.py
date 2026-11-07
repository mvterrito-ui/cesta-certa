import os

# Precisa vir antes de importar o app, porque as configurações são lidas uma vez.
# No CI, TEST_DATABASE_URL aponta para um PostgreSQL; localmente, usa SQLite.
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL", "sqlite:///./teste.db")
os.environ["JWT_SECRET"] = "segredo-apenas-para-testes-automatizados-0123456789"
os.environ["BCRYPT_ROUNDS"] = "4"
os.environ["AMBIENTE"] = "teste"

from datetime import timedelta  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Entrega, Familia, Usuario  # noqa: E402
from app.security import gerar_hash_senha  # noqa: E402
from app.tempo import agora_utc  # noqa: E402

SENHA = "Senha@Teste1"
CPF_ANTONIO = "12332165460"
CPF_MARIA = "98745678995"
CPF_ROSANA = "45698712328"


@pytest.fixture(autouse=True)
def banco_limpo():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    engine.dispose()


@pytest.fixture
def db():
    with SessionLocal() as sessao:
        yield sessao


@pytest.fixture
def client():
    return TestClient(app)


def criar_usuario(db, perfil="voluntario", email=None, ativo=True) -> Usuario:
    usuario = Usuario(
        nome="Coordenação" if perfil == "administrador" else "Juliana",
        email=email or f"{perfil}@teste.org.br",
        senha_hash=gerar_hash_senha(SENHA),
        perfil=perfil,
        ativo=ativo,
    )
    db.add(usuario)
    db.commit()
    return usuario


def criar_familia(db, usuario, nome="Antônio Carlos Silva", cpf=CPF_ANTONIO, status="ativa"):
    familia = Familia(
        nome_responsavel=nome,
        documento_responsavel=cpf,
        numero_integrantes=2,
        endereco="Rua das Palmeiras, 120 – Jd. Bandeirantes",
        status=status,
        cadastrado_por=usuario.id,
    )
    db.add(familia)
    db.commit()
    return familia


def criar_entrega_antiga(db, familia, usuario, dias_atras: int) -> Entrega:
    entrega = Entrega(
        familia_id=familia.id,
        usuario_id=usuario.id,
        data_entrega=agora_utc() - timedelta(days=dias_atras),
    )
    db.add(entrega)
    db.commit()
    return entrega


def autenticar(client, email) -> dict:
    resposta = client.post("/auth/login", json={"email": email, "senha": SENHA})
    assert resposta.status_code == 200, resposta.text
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}


@pytest.fixture
def voluntario(db):
    return criar_usuario(db, "voluntario")


@pytest.fixture
def administrador(db):
    return criar_usuario(db, "administrador")


@pytest.fixture
def auth_voluntario(client, voluntario):
    return autenticar(client, voluntario.email)


@pytest.fixture
def auth_admin(client, administrador):
    return autenticar(client, administrador.email)
