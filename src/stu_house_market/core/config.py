from pydantic_settings import BaseSettings, SettingsConfigDict
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
    RABBITMQ_USERNAME: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: str
    RABBITMQ_DB: str
    SAFE_URL_SECRET: str
    B2_APP_KEY_ID: str
    B2_APP_KEY: str
    B2_BUCKET: str
    B2_S3_ENDPOINT: str
    GOOGLE_OAUTH2_SCREEN_CLIENT_ID:str
    GOOGLE_OAUTH2_SCREEN_CLIENT_SECRET: str
    SESSION_SECRET: str
    DEFAULT_MIDDLEWARE_RATE_LIMIT: int

    
    model_config = SettingsConfigDict(env_file=".env-prod", extra="ignore")

settings = Settings()