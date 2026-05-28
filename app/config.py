from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIRECTORY = Path(__file__).resolve().parent.parent

class Config(BaseSettings):
    RIOT_API_KEY: str

    USER_DB: str
    PASSWORD_DB: str

    PLATFORM_HOST: dict = {
        "euw1": "euw1"
    }
    REGIONAL_HOST: dict = {
        "eu": "europe"
    }

    model_config = SettingsConfigDict(env_file=BASE_DIRECTORY / ".env", extra="ignore")

    @computed_field
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.USER_DB}:{self.PASSWORD_DB}@db:5432/riot_db"

config = Config()