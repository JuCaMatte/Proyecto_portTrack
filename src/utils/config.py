import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "DevOps Demo App"
    APP_VERSION: str = "1.0.0"
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = ENV == "development"

    # Database
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_NAME: str = os.getenv("DB_NAME", "app")

    # Logging
    LOG_LEVEL: str = "DEBUG" if DEBUG else "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
