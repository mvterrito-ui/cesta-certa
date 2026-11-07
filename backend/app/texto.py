import unicodedata


def normalizar_busca(texto: str) -> str:
    """Forma usada só para comparar nomes: sem acentos, minúsculas e espaços simples.

    "  Antônio  CARLOS " -> "antonio carlos"
    """
    decomposto = unicodedata.normalize("NFKD", texto or "")
    sem_acentos = "".join(c for c in decomposto if not unicodedata.combining(c))
    return " ".join(sem_acentos.casefold().split())
