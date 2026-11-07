"""Regra central do MVP (RF03): intervalo mínimo entre duas cestas para a mesma família.

Funções puras, sem banco de dados, para facilitar os testes unitários.
"""

from datetime import date, timedelta


def proxima_entrega(ultima: date, intervalo_dias: int) -> date:
    return ultima + timedelta(days=intervalo_dias)


def pode_receber(ultima: date | None, hoje: date, intervalo_dias: int) -> bool:
    if ultima is None:
        return True
    return hoje >= proxima_entrega(ultima, intervalo_dias)


def mensagem_bloqueio(ultima: date, intervalo_dias: int) -> str:
    proxima = proxima_entrega(ultima, intervalo_dias)
    return (
        f"Esta família já recebeu cesta em {ultima:%d/%m}. "
        f"Próxima entrega a partir de {proxima:%d/%m}."
    )
