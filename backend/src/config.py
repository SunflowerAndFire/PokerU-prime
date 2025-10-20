from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DOMAIN: str
    VERSION: str
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRY: int
    REFRESH_TOKEN_EXPIRY: int
    JTI_EXPIRY: int
    REDIS_PORT: int
    REDIS_HOST: str
    RESEND_API_KEY: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

Config = Settings()
