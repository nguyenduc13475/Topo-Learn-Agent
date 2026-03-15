from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str
    VERSION: str = "1.0.0"

    # Postgres Database variables
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    # Neo4j Database
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str

    # AI API Keys
    GEMINI_API_KEY: str

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Initialize global instance
settings = Settings()
