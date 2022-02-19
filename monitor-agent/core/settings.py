from pydantic import BaseSettings


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    metrics_URL: str = "http://httpbin.org/post"
    alerts_URL: str = ""
    post_task_interval: int = 60


settings = Settings()
