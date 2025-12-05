from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "booking-service"
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()
