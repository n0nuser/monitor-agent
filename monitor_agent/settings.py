import json
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

directory = Path(__file__).resolve().parent
abs_file_path = directory / "settings.json"
if not abs_file_path.exists():
    raise FileNotFoundError(f"File not found: {abs_file_path}")


class AlertsConfig(BaseModel):
    """Alerts for the monitor_agent application."""

    url: str


class AuthConfig(BaseModel):
    """Auth for the monitor_agent application."""

    agent_token: UUID
    name: str
    user_token: UUID


class EndpointsConfig(BaseModel):
    """Endpoints for the monitor_agent application."""

    agent_endpoint: str
    metric_endpoint: str


class LoggingConfig(BaseModel):
    """Logging for the monitor_agent application."""

    filename: str
    level: str


class MetricsConfig(BaseModel):
    """Metric config for the monitor_agent application."""

    enable_logfile: bool
    get_endpoint: bool
    log_filename: str
    post_interval: int


class ThresholdsConfig(BaseModel):
    """Thresholds for the monitor_agent application."""

    cpu_percent: int
    ram_percent: int


class UvicornConfig(BaseModel):
    """Uvicorn configuration."""

    backlog: int
    debug: bool
    host: str
    log_level: str
    port: int
    reload: bool
    timeout_keep_alive: int
    workers: int


class Settings(BaseSettings):
    """Settings for the monitor_agent application."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.prod"), env_file_encoding="utf-8"
    )
    alerts: AlertsConfig
    auth: AuthConfig
    endpoints: EndpointsConfig
    logging: LoggingConfig
    metrics: MetricsConfig
    thresholds: ThresholdsConfig
    uvicorn: UvicornConfig


SETTINGS = Settings.model_validate_json(json.dumps(abs_file_path))
