import pytest

from tests.conftest import SENHA, criar_usuario

pytestmark = pytest.mark.integracao


def test_login_valido_devolve_token_e_dados_do_usuario(client, voluntario):
    resposta = client.post("/auth/login", json={"email": voluntario.email, "senha": SENHA})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["token_type"] == "bearer"
    assert corpo["usuario"]["perfil"] == "voluntario"
    assert "senha_hash" not in corpo["usuario"]


def test_email_e_senha_errados_recebem_a_mesma_mensagem(client, voluntario):
    senha_errada = client.post("/auth/login", json={"email": voluntario.email, "senha": "errada"})
    email_errado = client.post("/auth/login", json={"email": "nao@existe.org.br", "senha": SENHA})
    assert senha_errada.status_code == email_errado.status_code == 401
    assert senha_errada.json()["detail"] == email_errado.json()["detail"]


def test_conta_bloqueada_apos_5_tentativas_falhas(client, voluntario):
    for _ in range(5):
        client.post("/auth/login", json={"email": voluntario.email, "senha": "errada"})
    # Mesmo com a senha certa, o login fica bloqueado por 15 minutos.
    resposta = client.post("/auth/login", json={"email": voluntario.email, "senha": SENHA})
    assert resposta.status_code == 429


def test_usuario_inativo_nao_consegue_entrar(client, db):
    inativo = criar_usuario(db, email="inativo@teste.org.br", ativo=False)
    resposta = client.post("/auth/login", json={"email": inativo.email, "senha": SENHA})
    assert resposta.status_code == 401


def test_rotas_protegidas_exigem_token(client):
    assert client.get("/auth/me").status_code == 401
    assert client.get("/familias", params={"busca": "silva"}).status_code == 401


def test_token_invalido_e_recusado(client):
    resposta = client.get("/auth/me", headers={"Authorization": "Bearer abc.def.ghi"})
    assert resposta.status_code == 401


def test_logout_invalida_o_token(client, auth_voluntario):
    assert client.get("/auth/me", headers=auth_voluntario).status_code == 200
    assert client.post("/auth/logout", headers=auth_voluntario).status_code == 204
    assert client.get("/auth/me", headers=auth_voluntario).status_code == 401


def test_somente_administrador_cria_usuarios(client, auth_voluntario, auth_admin):
    novo = {"nome": "Paulo", "email": "paulo@teste.org.br", "senha": "Senha@Forte1"}
    assert client.post("/usuarios", json=novo, headers=auth_voluntario).status_code == 403
    resposta = client.post("/usuarios", json=novo, headers=auth_admin)
    assert resposta.status_code == 201
    assert resposta.json()["perfil"] == "voluntario"


def test_saude_responde_ok(client):
    resposta = client.get("/saude")
    assert resposta.status_code == 200
    assert resposta.headers["X-Content-Type-Options"] == "nosniff"


def test_saude_aceita_head_usado_pelo_monitoramento(client):
    # O UptimeRobot gratuito verifica com HEAD; antes a rota respondia 405.
    resposta = client.head("/saude")
    assert resposta.status_code == 200
    assert resposta.content == b""
