import pytest

from tests.conftest import CPF_ANTONIO, CPF_MARIA, CPF_ROSANA, criar_familia

pytestmark = pytest.mark.integracao

NOVA_FAMILIA = {
    "nome_responsavel": "Antônio Carlos Silva",
    "documento_responsavel": "123.321.654-60",
    "endereco": "Rua das Palmeiras, 120 – Jd. Bandeirantes",
    "numero_integrantes": 2,
}


def test_cadastro_de_familia_guarda_cpf_so_com_digitos(client, auth_voluntario, db):
    resposta = client.post("/familias", json=NOVA_FAMILIA, headers=auth_voluntario)
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["cpf"] == "***.321.654-**"
    assert corpo["apta"] is True
    assert corpo["entregas"] == []


def test_cpf_duplicado_e_recusado_mesmo_com_nome_diferente(client, auth_voluntario):
    client.post("/familias", json=NOVA_FAMILIA, headers=auth_voluntario)
    repetida = {
        **NOVA_FAMILIA,
        "nome_responsavel": "Antonio C. Silva",
        "documento_responsavel": CPF_ANTONIO,
    }
    resposta = client.post("/familias", json=repetida, headers=auth_voluntario)
    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "Já existe uma família cadastrada com este CPF."


def test_cpf_invalido_devolve_mensagem_clara(client, auth_voluntario):
    invalida = {**NOVA_FAMILIA, "documento_responsavel": "123.321.654-00"}
    resposta = client.post("/familias", json=invalida, headers=auth_voluntario)
    assert resposta.status_code == 422
    erros = resposta.json()["erros"]
    assert erros[0]["campo"] == "documento_responsavel"
    assert erros[0]["mensagem"] == "CPF inválido. Confira os 11 números."


def test_numero_de_integrantes_precisa_ser_positivo(client, auth_voluntario):
    invalida = {**NOVA_FAMILIA, "numero_integrantes": 0}
    resposta = client.post("/familias", json=invalida, headers=auth_voluntario)
    assert resposta.status_code == 422


def test_busca_por_parte_do_nome_sem_diferenciar_maiusculas(
    client, auth_voluntario, db, voluntario
):
    criar_familia(db, voluntario, "Antônio Carlos Silva", CPF_ANTONIO)
    criar_familia(db, voluntario, "Maria José da Silva", CPF_MARIA)
    criar_familia(db, voluntario, "Rosana Lima", CPF_ROSANA)
    resposta = client.get("/familias", params={"busca": "SILVA"}, headers=auth_voluntario)
    assert resposta.status_code == 200
    nomes = [f["nome_responsavel"] for f in resposta.json()]
    assert nomes == ["Antônio Carlos Silva", "Maria José da Silva"]


def test_busca_pelo_cpf_completo_com_pontuacao(client, auth_voluntario, db, voluntario):
    criar_familia(db, voluntario, "Antônio Carlos Silva", CPF_ANTONIO)
    resposta = client.get("/familias", params={"busca": "123.321.654-60"}, headers=auth_voluntario)
    assert [f["nome_responsavel"] for f in resposta.json()] == ["Antônio Carlos Silva"]


@pytest.mark.parametrize("termo", ["", "Si", "12345"])
def test_busca_exige_3_letras_ou_cpf_completo(client, auth_voluntario, termo):
    resposta = client.get("/familias", params={"busca": termo}, headers=auth_voluntario)
    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "Digite pelo menos 3 letras ou o CPF completo."


def test_busca_nao_mostra_familias_inativas(client, auth_voluntario, db, voluntario):
    criar_familia(db, voluntario, "Antônio Carlos Silva", CPF_ANTONIO, status="inativa")
    resposta = client.get("/familias", params={"busca": "Antônio"}, headers=auth_voluntario)
    assert resposta.json() == []


@pytest.mark.parametrize("termo", ["' OR 1=1 --", "%%%", "silva'; DROP TABLE familia; --"])
def test_busca_trata_tentativa_de_injecao_como_texto(
    client, auth_voluntario, db, voluntario, termo
):
    criar_familia(db, voluntario)
    resposta = client.get("/familias", params={"busca": termo}, headers=auth_voluntario)
    assert resposta.status_code == 200
    assert resposta.json() == []
    # A tabela continua existindo e com os dados.
    assert client.get("/familias", params={"busca": "Silva"}, headers=auth_voluntario).json()


def test_administrador_ve_cpf_completo_e_voluntario_mascarado(
    client, auth_admin, auth_voluntario, db, voluntario
):
    familia = criar_familia(db, voluntario)
    admin = client.get(f"/familias/{familia.id}", headers=auth_admin).json()
    volunt = client.get(f"/familias/{familia.id}", headers=auth_voluntario).json()
    assert admin["cpf"] == "123.321.654-60"
    assert volunt["cpf"] == "***.321.654-**"


def test_familia_inexistente_devolve_404(client, auth_voluntario):
    resposta = client.get("/familias/9999", headers=auth_voluntario)
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Família não encontrada."
