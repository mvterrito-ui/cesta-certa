from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

from app.config import get_settings


def agora_utc() -> datetime:
    return datetime.now(UTC)


def como_utc(momento: datetime) -> datetime:
    """Alguns bancos (SQLite nos testes) devolvem datas sem fuso; assume UTC."""
    if momento.tzinfo is None:
        return momento.replace(tzinfo=UTC)
    return momento.astimezone(UTC)


def data_local(momento: datetime) -> date:
    """Data do calendário da associação (Londrina), usada na regra dos 15 dias."""
    return como_utc(momento).astimezone(ZoneInfo(get_settings().fuso_horario)).date()


def hoje_local() -> date:
    return data_local(agora_utc())
