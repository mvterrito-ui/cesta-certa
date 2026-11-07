from datetime import UTC, datetime

import pytest

from app.models import Entrega
from app.services.relatorio_service import periodo_do_mes
from tests.conftest import CPF_ANTONIO, CPF_MARIA, CPF_ROSANA, criar_familia, criar_usuario

pytestmark = pytest.mark.integracao


def registrar(db, familia, usuario, momento: datetime):
    db.add(Entrega(familia_id=familia.id, usuario_id=usuario.id, data_entrega=momento))
    db.commit()


@pytest.fixture
def outubro(db, voluntario, administrador):
    """Cenário fictício de outubro/2026 com entregas dentro e fora do mês."""
    paulo = criar_usuario(db, email="paulo@teste.org.br")
    paulo.nome = "Paulo"
    db.commit()
    antonio = criar_familia(db, voluntario, "Antônio Carlos Silva", CPF_ANTONIO)  # 2 pessoas
    maria = criar_familia(db, voluntario, "Maria José da Silva", CPF_MARIA)
    maria.numero_integrantes = 4
    criar_familia(db, voluntario, "Rosana Silva Lima", CPF_ROSANA)  # sem entrega em outubro
    db.commit()

    registrar(db, antonio, voluntario, datetime(2026, 10, 3, 13, 0, tzinfo=UTC))
    registrar(db, antonio, paulo, datetime(2026, 10, 24, 13, 0, tzinfo=UTC))
    # 01/11 às 02h UTC ainda é 31/10 às 23h em Londrina: conta em outubro.
    registrar(db, maria, voluntario, datetime(2026, 11, 1, 2, 0, tzinfo=UTC))
    # Fora de outubro.
    registrar(db, maria, voluntario, datetime(2026, 9, 30, 15, 0, tzinfo=UTC))
    registrar(db, maria, voluntario, datetime(2026, 11, 1, 4, 0, tzinfo=UTC))


def test_relatorio_mensal_soma_entregas_familias_e_pessoas(client, auth_admin, outubro):
    resposta = client.get("/relatorios/mensal", params={"ano": 2026, "mes": 10}, headers=auth_admin)
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total_entregas"] == 3
    assert corpo["familias_atendidas"] == 2
    assert corpo["pessoas_atendidas"] == 6
    assert corpo["familias_ativas"] == 3
    assert corpo["familias_sem_entrega"] == 1
    assert corpo["por_voluntario"] == [
        {"nome": "Juliana", "entregas": 2},
        {"nome": "Paulo", "entregas": 1},
    ]


def test_relatorio_de_mes_sem_entregas(client, auth_admin, outubro):
    resposta = client.get("/relatorios/mensal", params={"ano": 2026, "mes": 8}, headers=auth_admin)
    corpo = resposta.json()
    assert corpo["total_entregas"] == 0
    assert corpo["pessoas_atendidas"] == 0
    assert corpo["familias_sem_entrega"] == 3
    assert corpo["por_voluntario"] == []


def test_relatorio_e_exclusivo_da_coordenacao(client, auth_voluntario):
    resposta = client.get(
        "/relatorios/mensal", params={"ano": 2026, "mes": 10}, headers=auth_voluntario
    )
    assert resposta.status_code == 403
    assert resposta.json()["detail"] == "Esta função é exclusiva da coordenação."


@pytest.mark.parametrize("mes", [0, 13])
def test_mes_invalido_e_recusado(client, auth_admin, mes):
    params = {"ano": 2026, "mes": mes}
    resposta = client.get("/relatorios/mensal", params=params, headers=auth_admin)
    assert resposta.status_code == 422


def test_periodo_de_dezembro_termina_em_janeiro():
    inicio, fim = periodo_do_mes(2026, 12)
    assert inicio == datetime(2026, 12, 1, 3, 0, tzinfo=UTC)
    assert fim == datetime(2027, 1, 1, 3, 0, tzinfo=UTC)
