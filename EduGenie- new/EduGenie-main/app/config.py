from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = "EduGenie"
    environment: str = "development"

    host: str = "0.0.0.0"
    port: int = 8000

    # Gemini
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.8-flash"

    # Optional local explanation model
    local_explanation_model: str = "MBZUAI/LaMini-Flan-T5-783M"
    use_local_explanation_model: bool = False

    # Application limits
    max_input_chars: int = 20000

    # CORS
    cors_origins: str = (
        "http://127.0.0.1:8000,"
        "http://localhost:8000,"
        "http://0.0.0.0:8000"
    )

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()