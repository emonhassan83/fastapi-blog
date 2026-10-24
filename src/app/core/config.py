from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(validation_alias="APP_NAME")
    database_url: str = Field(validation_alias="DATABASE_URL")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
