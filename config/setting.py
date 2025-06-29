from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # JWT Security
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Payment URLs
    PAYMENT_BASE_URL: str
    PAYMENT_CALLBACK_URL: str
    PAYMENT_REDIRECT_URL: str

    # API Settings
    API_HOST: str
    API_PORT: int
    DEBUG: bool

    class Config:
        env_file = ".env"  # Load from .env

settings = Settings()
