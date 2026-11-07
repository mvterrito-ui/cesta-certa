from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.config import get_settings
from app.repositories import relatorio_repo
from app.schemas import EntregasPorVoluntario, RelatorioMensal


def periodo_do_mes(ano: int, mes: int) -> tuple[datetime, datetime]:
    """Início e fim (exclusivo) do mês no horário de Londrina, convertidos para UTC."""
    fuso = ZoneInfo(get_settings().fuso_horario)
    inicio = datetime(ano, mes, 1, tzinfo=fuso)
    ano_fim, mes_fim = (ano + 1, 1) if mes == 12 else (ano, mes + 1)
    fim = datetime(ano_fim, mes_fim, 1, tzinfo=fuso)
    return inicio.astimezone(UTC), fim.astimezone(UTC)


def mensal(db: Session, ano: int, mes: int) -> RelatorioMensal:
    """RF04: números do mês para a prestação de contas da associação."""
    inicio, fim = periodo_do_mes(ano, mes)
    familias, pessoas = relatorio_repo.familias_atendidas(db, inicio, fim)
    ativas, sem_entrega = relatorio_repo.familias_ativas_sem_entrega(db, inicio, fim)
    return RelatorioMensal(
        ano=ano,
        mes=mes,
        total_entregas=relatorio_repo.total_entregas(db, inicio, fim),
        familias_atendidas=familias,
        pessoas_atendidas=pessoas,
        familias_ativas=ativas,
        familias_sem_entrega=sem_entrega,
        por_voluntario=[
            EntregasPorVoluntario(nome=nome, entregas=total)
            for nome, total in relatorio_repo.entregas_por_voluntario(db, inicio, fim)
        ],
    )
