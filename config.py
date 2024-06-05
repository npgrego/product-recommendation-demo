from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    app_username: str
    app_password: str
    app_server: str = "https://product-recommendation.onlydata.click"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


app_settings = AppSettings()