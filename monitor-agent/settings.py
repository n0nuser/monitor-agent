from pydantic import BaseSettings

# https://www.uvicorn.org/settings/
class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    reload: bool = True
    debug: bool = True
    log_level: str = "trace"

    ssl_keyfile: str = None
    ssl_keyfile_password: str = None
    ssl_certfile: str = None
    ssl_version: int = 3
    ssl_cert_reqs: int = None
    ssl_ca_certs: str = None
    ssl_ciphers: str = "TLSv1"

    limit_concurrency: int = None
    limit_max_requests: int = None
    backlog: int = 2048

    timeout_keep_alive: int = 5

    metrics_endpoint: bool = True
    metrics_URL: str = "http://httpbin.org/post"
    post_task_interval: int = 60
    # metrics_file: str = "metrics.json"

    alerts_URL: str = ""


settings = Settings()
