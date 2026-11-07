import re


def somente_digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


def cpf_valido(valor: str) -> bool:
    """Valida tamanho e dígitos verificadores do CPF."""
    cpf = somente_digitos(valor)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for tamanho in (9, 10):
        soma = sum(int(cpf[i]) * (tamanho + 1 - i) for i in range(tamanho))
        digito = (soma * 10) % 11 % 10
        if digito != int(cpf[tamanho]):
            return False
    return True


def formatar_cpf(cpf: str) -> str:
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def mascarar_cpf(cpf: str) -> str:
    """Mantém só os dígitos centrais visíveis: ***.321.654-** (RNF02)."""
    return f"***.{cpf[3:6]}.{cpf[6:9]}-**"
