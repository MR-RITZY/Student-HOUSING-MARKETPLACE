from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BASE_URL: str
    APP_NAME: str 
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
    REDIS_SSL_ENABLED: bool = False      
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()