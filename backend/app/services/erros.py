class ErroDeNegocio(Exception):
    """Erro esperado, com mensagem pronta para o usuário e status HTTP."""

    def __init__(self, mensagem: str, status: int = 400, **dados):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status
        self.dados = dados


class NaoEncontrado(ErroDeNegocio):
    def __init__(self, mensagem: str):
        super().__init__(mensagem, status=404)


class Conflito(ErroDeNegocio):
    def __init__(self, mensagem: str, **dados):
        super().__init__(mensagem, status=409, **dados)
