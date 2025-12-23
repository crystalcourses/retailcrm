from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    retailcrm_url: str
    retailcrm_api_key: str
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()