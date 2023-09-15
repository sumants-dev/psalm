import os
from pydantic_settings import BaseSettings, SettingsConfigDict
    
class Settings(BaseSettings):
    app_name: str = "Pontus PSaLM"
    open_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anonymizer_key: str = os.getenv("ANONYMIZER_API_KEY", "")
    postgres_cnxn_str: str = os.getenv("POSTGRES_CNXN_STR", "")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


