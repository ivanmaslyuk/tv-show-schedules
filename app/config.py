from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/tvshows"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expiry_minutes: int = 60 * 24


settings = Settings()

