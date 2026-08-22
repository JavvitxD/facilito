from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://invdoc:invdoc123@localhost:5432/invdoc"
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Origenes permitidos para CORS, separados por coma. "*" permite todos.
    CORS_ORIGINS: str = "*"

    # Ruta al frontend compilado. Si existe, FastAPI lo sirve como SPA.
    STATIC_DIR: str = "/app/static"

    @field_validator("DATABASE_URL")
    @classmethod
    def normalizar_url(cls, v: str) -> str:
        # Railway/Render/Heroku entregan "postgres://", SQLAlchemy 2 exige "postgresql://"
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"


settings = Settings()
