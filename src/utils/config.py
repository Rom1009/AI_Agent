from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, EmailStr
from enum import Enum

class EnvMode(str, Enum):
    DEV: str = "development"
    PROD: str = "production"
    STAGING: str = "staging"
    TEST: str = "testing"

class Settings(BaseSettings):
    # COMMON GLOBALS
    DEBUG: bool = False
    MODEL_NAME: str = "llama-3.1-8b-instant" 
    LOG_LEVEL: str = "INFO"
    ENV_MODE: EnvMode = EnvMode.DEV
    CONFIG_PATH: str = "config/input.yml"
    IMG_PATH: str = "public/images"
    DATABASE_URL: str = "sqlite:///./digest.db"

    # ENVIRONMENT VARIABLES
    GROQ_API_KEY: SecretStr

    MAIL_SENDER: EmailStr
    MAIL_RECEIVER: EmailStr
    MAIL_PASSWORD: SecretStr

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore",
    )


settings = Settings()
