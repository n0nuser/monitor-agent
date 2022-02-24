import os
import json
from types import SimpleNamespace
from pydantic import BaseSettings

# https://www.uvicorn.org/settings/
class SettingsPydantic(BaseSettings):
    host: str
    port: int
    workers: int
    reload: bool
    debug: bool
    log_level: str
    ssl_keyfile: str | None = None
    ssl_keyfile_password: str | None = None
    ssl_certfile: str | None = None
    ssl_version: int | None = None
    ssl_cert_reqs: int | None = None
    ssl_ca_certs: str | None = None
    ssl_ciphers: str | None = None
    limit_concurrency: int
    limit_max_requests: int
    backlog: int
    timeout_keep_alive: int
    metric_endpoint: bool
    post_metric_url: str
    post_interval: int
    metric_enable_file: bool
    metric_file: str
    alerts_URL: str


class Settings:
    def __init__(self, rel_path: str = "settings.json"):
        dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        self.abs_file_path = os.path.join(dir, rel_path)
        self.settings = self.read_settings()

    def read_settings(self):
        f = open(self.abs_file_path, "r")
        data = f.read()
        # Parse JSON into an object with attributes corresponding to dict keys.
        # https://stackoverflow.com/a/15882054
        return json.loads(data, object_hook=lambda d: SimpleNamespace(**d))

    def write_settings(self, new_data):
        try:
            json.loads(new_data)
        except json.JSONDecodeError as msg:
            return {"status": msg.msg, "data": new_data}
        f = open(self.abs_file_path, "w")
        f.write(new_data)
        self.settings = self.read_settings()
        return {"status": "success", "data": new_data}
