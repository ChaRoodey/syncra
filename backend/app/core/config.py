import os
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent
ENV_FILE = os.getenv("ENV_FILE", ".env")


class AuthJWT(BaseModel):
    private_key: str = Path(BASE_DIR / "certs" / "jwt-private.pem").read_text()
    public_key: str = Path(BASE_DIR / "certs" / "jwt-public.pem").read_text()
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 60 * 24 * 7


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5532
    POSTGRES_DB: str = "syncra_db"
    POSTGRES_USER: str = "syncra_user"
    POSTGRES_PASSWORD: str = "syncra_user"

    LOG_LEVEL: str = "INFO"

    auth_jwt: AuthJWT = AuthJWT()

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
