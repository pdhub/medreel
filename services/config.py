from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MEDREEL_", env_file=".env", extra="ignore")

    data_dir: Path = Path("/data")
    max_upload_mb: int = 500
    whisper_model: str = "base"
    whisper_compute_type: str = "int8"
    anthropic_api_key: str | None = Field(default=None, validation_alias="ANTHROPIC_API_KEY")
    anthropic_model: str = "claude-opus-5-5"
    worker_poll_seconds: float = 1.0
    log_level: str = "INFO"


settings = Settings()
