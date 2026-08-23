from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "Sentinel AI"
    app_version: str = "0.1.0"
    database_url: str = "sqlite:///./sentinel.db"
    debug: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()