from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://bonyan:bonyan123@localhost:5432/bonyan_core"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    APP_NAME: str = "Bonyan Core"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    SQL_ECHO: bool = False
    AUTO_CREATE_TABLES: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
