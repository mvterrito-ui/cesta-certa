from datetime import date, timedelta

import pytest

from app.tempo import hoje_local
from tests.conftest import criar_entrega_antiga, criar_familia

pytestmark = pytest.mark.integracao


def test_registra_entrega_para_familia_sem_historico(client, auth_voluntario, db, voluntario):
    familia = criar_familia(db, voluntario)
    resposta = client.post(f"/familias/{familia.id}/entregas", headers=auth_voluntario)
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["nome_responsavel"] == "Antônio Carlos Silva"
    assert corpo["proxima_entrega"] == (hoje_local() + timedelta(days=15)).isoformat()


def test_segunda_entrega_no_mesmo_dia_e_bloqueada(client, auth_voluntario, db, voluntario):
    familia = criar_familia(db, voluntario)
    client.post(f"/familias/{familia.id}/entregas", headers=auth_voluntario)
    resposta = client.post(f"/familias/{familia.id}/entregas", headers=auth_voluntario)

    assert resposta.status_code == 409
    corpo = resposta.json()
    hoje = hoje_local()
    proxima = hoje + timedelta(days=15)
    assert corpo["detail"] == (
        f"Esta família já recebeu cesta em {hoje:%d/%m}. "
        f"Próxima entrega a partir de {proxima:%d/%m}."
    )
    assert corpo["ultima_entrega"] == hoje.isoformat()
    assert corpo["proxima_entrega"] == proxima.isoformat()


def test_bloqueio_nao_grava_nova_entrega(client, auth_voluntario, db, voluntario):
    familia = criar_familia(db, voluntario)
    criar_entrega_antiga(db, familia, voluntario, dias_atras=5)
    client.post(f"/familias/{familia.id}/entregas", headers=auth_voluntario)
    detalhe = client.get(f"/familias/{familia.id}", headers=auth_voluntario).json()
    assert len(detalhe["entregas"]) == 1
    assert detalhe["apta"] is False


def test_familia_com_entrega_ha_15_dias_pode_receber(client, auth_voluntario, db, voluntario):
    familia = criar_familia(db, voluntario)
    criar_entrega_antiga(db, familia, voluntario, dias_atras=15)
    resposta = client.post(f"/familias/{familia.id}/entregas", headers=auth_voluntario)
    assert resposta.status_code == 201


def test_familia_com_entrega_ha_14_dias_e_bloqueada(client, auth_voluntario, db, voluntario):
    familia = criar_familia(db, voluntario)
    criar_entrega_antiga(db, familia, voluntario, dias_atras=14)
    resposta = client.post(f"/familias/{familia.id}/entregas", headers=auth_voluntario)
    assert resposta.status_code == 409


def test_busca_mostra_ultima_cesta_e_se_esta_apta(client, auth_voluntario, db, voluntario):
    familia = criar_familia(db, voluntario)
    criar_entrega_antiga(db, familia, voluntario, dias_atras=20)
    criar_entrega_antiga(db, familia, voluntario, dias_atras=5)
    [item] = client.get("/familias", params={"busca": "Antônio"}, headers=auth_voluntario).json()
    assert date.fromisoformat(item["ultima_entrega"]) == hoje_local() - timedelta(days=5)
    assert item["apta"] is False


def test_historico_mostra_quem_registrou(client, auth_voluntario, db, voluntario):
    familia = criar_familia(db, voluntario)
    client.post(f"/familias/{familia.id}/entregas", headers=auth_voluntario)
    detalhe = client.get(f"/familias/{familia.id}", headers=auth_voluntario).json()
    assert detalhe["entregas"][0]["registrado_por"] == "Juliana"


def test_familia_inativa_nao_recebe_entrega(client, auth_voluntario, db, voluntario):
    familia = criar_familia(db, voluntario, status="inativa")
    resposta = client.post(f"/familias/{familia.id}/entregas", headers=auth_voluntario)
    assert resposta.status_code == 409


def test_entrega_para_familia_inexistente(client, auth_voluntario):
    assert client.post("/familias/9999/entregas", headers=auth_voluntario).status_code == 404


def test_registrar_entrega_exige_login(client, db, voluntario):
    familia = criar_familia(db, voluntario)
    assert client.post(f"/familias/{familia.id}/entregas").status_code == 401
