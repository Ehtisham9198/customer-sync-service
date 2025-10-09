from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str | None = None


    KAFKA_BROKER_URL: str = "localhost:9092"
    KAFKA_CUSTOMER_TOPIC: str = "customer_events"

    ENV: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
