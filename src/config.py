from functools import lru_cache
from pathlib import Path
from typing import Optional

import pem
from dotenv import load_dotenv
from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import pytz


class Config(BaseSettings):
    DATABASE_URL: str = ''

    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: SecretStr
    DB_PASS: SecretStr

    TIMEZONE: pytz.BaseTzInfo = pytz.timezone('Europe/Moscow')

    JWT_PUBLIC_KEY_PATH: str
    JWT_PRIVATE_KEY_PATH: str
    JWT_PRIVATE_KEY: SecretStr
    JWT_PUBLIC_KEY: SecretStr
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    API_HOST: str
    API_PORT: int

    SSL_CERT_PATH: str
    SSL_PRIVATE_KEY_PATH: str

    LOG_LVL: str
    LOGS_PATH: str
    LOG_NAME: str

    TAP_BANK_BASE_URL: str
    TAP_BANK_API_TOKEN: str

    model_config = SettingsConfigDict(env_file='.env')

    def __init__(self, _env_file: Optional[str] = None, **kwargs):
        if not _env_file:
            _env_file = str(Path(__file__).parent.parent / '.env')
        load_dotenv(_env_file, override=True)
        super().__init__(**kwargs)

        self.DATABASE_URL = (
            f'postgresql+asyncpg://'
            f'{self.DB_USER.get_secret_value()}:{self.DB_PASS.get_secret_value()}@'
            f'{self.DB_HOST}:{self.DB_PORT}'
            f'/{self.DB_NAME}'
        )

    @model_validator(mode='before')
    def set_attributes(cls, values) -> dict:
        values['JWT_PRIVATE_KEY'] = SecretStr(str(pem.parse_file(values["JWT_PRIVATE_KEY_PATH"])[0]))
        values['JWT_PUBLIC_KEY'] = SecretStr(str(pem.parse_file(values["JWT_PUBLIC_KEY_PATH"])[0]))

        return values


@lru_cache
def get_config():
    return Config()
