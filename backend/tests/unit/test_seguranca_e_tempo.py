from datetime import UTC, date, datetime, timedelta

import jwt
import pytest

from app.config import get_settings
from app.security import criar_token, decodificar_token, gerar_hash_senha, verificar_senha
from app.tempo import data_local


def test_hash_de_senha_nao_guarda_texto_simples():
    senha_hash = gerar_hash_senha("Senha@123")
    assert "Senha@123" not in senha_hash
    assert senha_hash.startswith("$2")


def test_verificar_senha_correta_e_incorreta():
    senha_hash = gerar_hash_senha("Senha@123")
    assert verificar_senha("Senha@123", senha_hash)
    assert not verificar_senha("senha@123", senha_hash)


def test_token_contem_usuario_perfil_e_versao():
    payload = decodificar_token(criar_token(7, "voluntario", 3))
    assert payload["sub"] == "7"
    assert payload["perfil"] == "voluntario"
    assert payload["ver"] == 3


def test_token_expira_em_8_horas():
    payload = decodificar_token(criar_token(1, "voluntario", 0))
    assert payload["exp"] - payload["iat"] == 8 * 3600


def test_token_expirado_e_recusado():
    settings = get_settings()
    vencido = jwt.encode(
        {"sub": "1", "exp": datetime.now(UTC) - timedelta(minutes=1)},
        settings.jwt_secret,
        algorithm="HS256",
    )
    with pytest.raises(jwt.ExpiredSignatureError):
        decodificar_token(vencido)


def test_token_assinado_com_outra_chave_e_recusado():
    falso = jwt.encode({"sub": "1", "perfil": "administrador"}, "x" * 40, algorithm="HS256")
    with pytest.raises(jwt.InvalidSignatureError):
        decodificar_token(falso)


def test_data_local_usa_horario_de_londrina():
    # 02h UTC do dia 24 ainda é dia 23 em Londrina (UTC-3).
    assert data_local(datetime(2026, 10, 24, 2, 0, tzinfo=UTC)) == date(2026, 10, 23)


def test_data_local_aceita_data_sem_fuso():
    assert data_local(datetime(2026, 10, 24, 15, 0)) == date(2026, 10, 24)
