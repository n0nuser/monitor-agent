import sys
import json
import uvicorn
import logging
from fastapi import FastAPI, UploadFile, File
from fastapi_utils.tasks import repeat_every
from .settings import Settings
from .core.metricFunctions import send_metrics, send_metrics_adapter, static, dynamic
from .core.command import Command

try:
    config_file = Settings()
except json.decoder.JSONDecodeError as msg:
    print('Error in "settings.json".', msg, file=sys.stderr)
    exit()

logger = logging.getLogger(__name__)
api = FastAPI()

endpoints = {
    "root": "/",
    "command": "/command",
    "metrics_endpoint": "/metrics",
    "settings": "/settings",
}

# GET
@api.get(endpoints["root"])
async def root():
    return {"message": "Hello World"}


@api.get(endpoints["settings"])
async def mod_settings():
    # if token:
    #     blablabla
    return config_file.read_settings_file(config_file.abs_file_path)


if config_file.settings.metric_endpoint:

    @api.get(endpoints["metrics_endpoint"])
    async def metrics_endpoint():
        elapsed_time, data = send_metrics_adapter([static, dynamic])
        return {"data": data, "elapsed_time": elapsed_time}


# POST
@api.post(endpoints["command"])
async def command(command: str, timeout: int):
    # if token:
    #     blablabla
    return Command(command, timeout).__dict__


@api.post(endpoints["settings"])
async def mod_settings(settings: UploadFile):
    # if token:
    #     blablabla
    data: str = settings.file.read().decode()
    return config_file.write_settings(data)


@api.on_event("startup")
@repeat_every(
    seconds=config_file.settings.post_interval, logger=logger, wait_first=True
)
def periodic():
    # https://github.com/tiangolo/fastapi/issues/520
    # https://fastapi-utils.davidmontague.xyz/user-guide/repeated-tasks/#the-repeat_every-decorator
    # Changed Timeloop for this
    elapsed_time, data = send_metrics_adapter([static, dynamic])
    send_metrics(
        url=config_file.settings.post_metric_url,
        elapsed_time=elapsed_time,
        data=data,
        file_enabled=config_file.settings.metric_enable_file,
        file_path=config_file.abs_file_path,
    )


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run(
        "monitor_agent.main:api",
        host=config_file.settings.host,
        port=config_file.settings.port,
        reload=config_file.settings.reload,
        workers=config_file.settings.workers,
        log_level=config_file.settings.log_level,
        interface="asgi3",
        debug=config_file.settings.debug,
        backlog=config_file.settings.backlog,
        timeout_keep_alive=config_file.settings.timeout_keep_alive,
        limit_concurrency=config_file.settings.limit_concurrency,
        limit_max_requests=config_file.settings.limit_max_requests,
        ssl_keyfile=config_file.settings.ssl_keyfile,
        ssl_keyfile_password=config_file.settings.ssl_keyfile_password,
        ssl_certfile=config_file.settings.ssl_certfile,
        ssl_version=config_file.settings.ssl_version,
        ssl_cert_reqs=config_file.settings.ssl_cert_reqs,
        ssl_ca_certs=config_file.settings.ssl_ca_certs,
        ssl_ciphers=config_file.settings.ssl_ciphers,
    )
