from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn

    
class Settings(BaseSettings):
    app_name: str = "Pontus PSaLM"
    postgres_db_uri: PostgresDsn | None  = None
    model_config = SettingsConfigDict(env_file=".env")
