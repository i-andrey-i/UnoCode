import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    CLIENT_ID: str | None = None
    CLIENT_SECRET: str | None = None
    CERT_PATH: str | None = None
    KEY_PATH: str | None = None
    TOKEN_URL: str | None = None
    API_BASE_URL: str | None = None
    DATABASE_PATH: str | None = None
    SCOPE: str | None = None
    class Config:
        env_file = ".env"
        env_prefix = "ALFA_"

settings = Settings()

