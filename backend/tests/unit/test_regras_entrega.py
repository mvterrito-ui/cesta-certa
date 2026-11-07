from datetime import date

from app.services.regras_entrega import mensagem_bloqueio, pode_receber, proxima_entrega

INTERVALO = 15


def test_familia_sem_entrega_pode_receber():
    assert pode_receber(None, date(2026, 10, 24), INTERVALO)


def test_familia_com_entrega_ha_14_dias_nao_pode_receber():
    assert not pode_receber(date(2026, 10, 10), date(2026, 10, 24), INTERVALO)


def test_familia_com_entrega_ha_exatos_15_dias_pode_receber():
    assert pode_receber(date(2026, 10, 9), date(2026, 10, 24), INTERVALO)


def test_entrega_no_mesmo_dia_e_bloqueada():
    assert not pode_receber(date(2026, 10, 24), date(2026, 10, 24), INTERVALO)


def test_proxima_entrega_soma_o_intervalo():
    assert proxima_entrega(date(2026, 10, 12), INTERVALO) == date(2026, 10, 27)


def test_proxima_entrega_atravessa_o_mes():
    assert proxima_entrega(date(2026, 10, 24), INTERVALO) == date(2026, 11, 8)


def test_mensagem_de_bloqueio_igual_a_especificada_no_rf03():
    assert mensagem_bloqueio(date(2026, 10, 12), INTERVALO) == (
        "Esta família já recebeu cesta em 12/10. Próxima entrega a partir de 27/10."
    )
