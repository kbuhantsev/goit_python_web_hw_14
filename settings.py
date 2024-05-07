from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # DB
    user: str
    password: str
    db_name: str = "contacts"
    domain: str = "localhost"
    port: str = "5432"

    # MAIL
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    mail_from_name: str

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # REDIS
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # CLOUDINARY
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    @staticmethod
    def get_uri():
        return f"postgresql+asyncpg://{settings.user}:{settings.password}@{settings.domain}:{settings.port}/{settings.db_name}"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
