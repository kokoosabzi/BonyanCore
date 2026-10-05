from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql://bonyan:bonyan123@localhost:5432/bonyan_core"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    APP_NAME: str = "Bonyan Core"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    SQL_ECHO: bool = False
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    AUTO_CREATE_SCHEMA: bool = True
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "admin"
    DEFAULT_ADMIN_FULL_NAME: str = "System Administrator"
    SESSION_COOKIE_SECURE: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/bonyancore.log"

    @model_validator(mode="after")
    def validate_production_secret(self):
        if not self.DEBUG and self.SECRET_KEY == "your-secret-key-change-in-production":
            raise ValueError("SECRET_KEY must be changed when DEBUG is disabled")
        if not self.DEBUG and self.DEFAULT_ADMIN_PASSWORD == "admin":
            raise ValueError("DEFAULT_ADMIN_PASSWORD must be changed when DEBUG is disabled")
        return self

settings = Settings()
