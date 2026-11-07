"""Cria as tabelas e carrega usuários e famílias FICTÍCIOS para desenvolvimento e testes de campo.

Uso: python -m app.seed
As senhas iniciais vêm das variáveis SEED_SENHA_ADMIN e SEED_SENHA_VOLUNTARIO.
"""

import os
from datetime import timedelta

from app.database import Base, SessionLocal, engine
from app.models import Entrega, Familia, Usuario
from app.security import gerar_hash_senha
from app.tempo import agora_utc

FAMILIAS = [
    # nome, CPF fictício (válido), integrantes, endereço, dias desde a última cesta
    ("Antônio Carlos Silva", "12332165460", 2, "Rua das Palmeiras, 120 – Jd. Bandeirantes", 23),
    ("Maria José da Silva", "98745678995", 4, "Rua dos Ipês, 45 – Jd. Bandeirantes", 5),
    ("Rosana Silva Lima", "45698712328", 5, "Av. Bandeirantes, 890 – Jd. Bandeirantes", None),
]


def executar() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.query(Usuario).count():
            print("Banco já possui dados; nada foi alterado.")
            return

        admin = Usuario(
            nome="Maria Aparecida",
            email="coordenacao@cestacerta.org.br",
            senha_hash=gerar_hash_senha(os.environ.get("SEED_SENHA_ADMIN", "Troque@Admin1")),
            perfil="administrador",
        )
        voluntaria = Usuario(
            nome="Juliana",
            email="juliana@cestacerta.org.br",
            senha_hash=gerar_hash_senha(os.environ.get("SEED_SENHA_VOLUNTARIO", "Troque@Volunt1")),
            perfil="voluntario",
        )
        db.add_all([admin, voluntaria])
        db.flush()

        agora = agora_utc()
        for nome, cpf, pessoas, endereco, dias in FAMILIAS:
            familia = Familia(
                nome_responsavel=nome,
                documento_responsavel=cpf,
                numero_integrantes=pessoas,
                endereco=endereco,
                cadastrado_por=admin.id,
            )
            db.add(familia)
            db.flush()
            if dias is not None:
                db.add(
                    Entrega(
                        familia_id=familia.id,
                        usuario_id=voluntaria.id,
                        data_entrega=agora - timedelta(days=dias),
                    )
                )
        db.commit()
        print("Dados fictícios carregados.")


if __name__ == "__main__":
    executar()
