from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(validation_alias="APP_NAME")
    database_url: str = Field(validation_alias="DATABASE_URL")

    # JWT Authentication Configuration
    jwt_secret_key: str = Field(
        validation_alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: str = Field(
        validation_alias="JWT_ALGORITHM",
    )
    jwt_access_token_expire_minutes: int = Field(
        validation_alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
