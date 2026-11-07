import pytest

from app.cpf import cpf_valido, formatar_cpf, mascarar_cpf, somente_digitos


@pytest.mark.parametrize("cpf", ["123.321.654-60", "12332165460", "987.456.789-95"])
def test_cpf_valido_aceita_com_e_sem_pontuacao(cpf):
    assert cpf_valido(cpf)


@pytest.mark.parametrize(
    "cpf",
    [
        "123.321.654-61",  # dígito verificador errado
        "111.111.111-11",  # todos os dígitos iguais
        "1233216546",  # 10 dígitos
        "",
        "abc.def.ghi-jk",
    ],
)
def test_cpf_invalido_e_recusado(cpf):
    assert not cpf_valido(cpf)


def test_somente_digitos_remove_pontuacao():
    assert somente_digitos("123.321.654-60") == "12332165460"


def test_mascara_mostra_apenas_digitos_centrais():
    assert mascarar_cpf("12332165460") == "***.321.654-**"


def test_formatar_cpf_completo():
    assert formatar_cpf("12332165460") == "123.321.654-60"
