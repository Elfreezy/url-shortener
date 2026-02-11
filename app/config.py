import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_NAME: str = "my_database.db"
    GLOBAL_PATH: str = os.path.join(os.path.dirname(__file__), "..")

    model_config = SettingsConfigDict(env_file=os.path.join(GLOBAL_PATH, ".env"))


settings = Settings()