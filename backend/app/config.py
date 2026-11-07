from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações lidas de variáveis de ambiente (ou do arquivo .env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ambiente: str = "desenvolvimento"  # desenvolvimento | producao
    database_url: str = "postgresql+psycopg://cesta:cesta@localhost:5432/cesta_certa"

    jwt_secret: str = "troque-esta-chave-em-producao"
    jwt_algoritmo: str = "HS256"
    jwt_expiracao_horas: int = 8

    bcrypt_rounds: int = 12
    max_tentativas_login: int = 5
    bloqueio_minutos: int = 15

    intervalo_entrega_dias: int = 15
    fuso_horario: str = "America/Sao_Paulo"

    cors_origins: str = "http://localhost:4200"

    @property
    def em_producao(self) -> bool:
        return self.ambiente == "producao"

    @property
    def lista_cors(self) -> list[str]:
        return [origem.strip() for origem in self.cors_origins.split(",") if origem.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
