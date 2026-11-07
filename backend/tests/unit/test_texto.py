import pytest

from app.texto import normalizar_busca


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("Antônio Carlos Silva", "antonio carlos silva"),
        ("MARIA JOSÉ", "maria jose"),
        ("  Conceição   da  Luz ", "conceicao da luz"),
        ("Ângela Müller", "angela muller"),
        ("", ""),
    ],
)
def test_normalizar_busca_remove_acentos_maiusculas_e_espacos(entrada, esperado):
    assert normalizar_busca(entrada) == esperado


def test_normalizar_busca_preserva_caracteres_especiais_como_texto():
    # % e _ continuam no termo; o repositório os escapa antes do LIKE.
    assert normalizar_busca("50%_Á") == "50%_a"
