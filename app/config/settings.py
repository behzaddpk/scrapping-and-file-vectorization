import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import SecretStr

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # db_database_url: SecretStr = SecretStr(os.getenv("DATABASE_URL"))
    open_api_key: SecretStr = SecretStr(os.getenv("OPEN_API_KEY"))

    class Config:
        env_file = ".env"

settings = Settings()

# DATABASE_URL = settings.db_database_url
