from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    app_username: str
    app_password: str
    app_server: str

    serp_api_key: str
    max_candidates: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


app_settings = AppSettings()