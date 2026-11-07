import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routers import auth, familias, saude
from app.services.erros import ErroDeNegocio

logger = logging.getLogger("cesta_certa")


def criar_app() -> FastAPI:
    settings = get_settings()
    # Documentação interativa desligada em produção (RNF02).
    docs = None if settings.em_producao else "/docs"
    app = FastAPI(title="Cesta Certa API", version="1.0.0", docs_url=docs, redoc_url=None)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.lista_cors,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.middleware("http")
    async def cabecalhos_seguranca(request: Request, call_next):
        resposta = await call_next(request)
        resposta.headers["X-Content-Type-Options"] = "nosniff"
        resposta.headers["X-Frame-Options"] = "DENY"
        resposta.headers["Referrer-Policy"] = "no-referrer"
        return resposta

    @app.exception_handler(ErroDeNegocio)
    async def erro_de_negocio(_: Request, erro: ErroDeNegocio):
        return JSONResponse(
            status_code=erro.status, content={"detail": erro.mensagem, **erro.dados}
        )

    @app.exception_handler(RequestValidationError)
    async def erro_de_validacao(_: Request, erro: RequestValidationError):
        erros = [
            {
                "campo": str(e["loc"][-1]),
                "mensagem": str(e["msg"]).removeprefix("Value error, "),
            }
            for e in erro.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={"detail": "Confira os campos destacados.", "erros": erros},
        )

    @app.exception_handler(Exception)
    async def erro_inesperado(_: Request, erro: Exception):
        # Detalhes vão só para o log; o usuário recebe mensagem genérica (RNF02).
        logger.exception("Erro inesperado", exc_info=erro)
        return JSONResponse(
            status_code=500,
            content={"detail": "Não foi possível concluir agora. Tente novamente."},
        )

    app.include_router(saude.router)
    app.include_router(auth.router)
    app.include_router(familias.router)
    return app


app = criar_app()
