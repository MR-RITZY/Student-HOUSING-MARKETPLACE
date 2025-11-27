from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr
from typing import Literal

class Settings(BaseSettings):
    BASE_URL: str
    FRONTEND_HOST: str
    APP_NAME: str
    ENV: Literal["DEV", "PROD"]
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXP: int
    JWT_REFRESH_TOKEN_EXP: int
    REDIS_HOST: str 
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str
    REDIS_USERNAME: str
    RABBITMQ_HOST: str 
    RABBITMQ_PORT: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_USERNAME: str
    SAFE_URL_SECRET: str
    RESEND_API_KEY: str

    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()