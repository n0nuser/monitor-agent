import sys
import json
import uvicorn
import logging
import requests
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
    "metrics": "/metrics",
    "settings": "/settings",
    "thresholds": "/thresholds",
}

thresholds = {
    "cpu_percent": 50,
    "ram_percent": 30,
}

# GET
@api.get(endpoints["root"])
async def root():
    return {"endpoints": endpoints}


@api.get(endpoints["thresholds"])
async def thresholds():
    return {"thresholds": thresholds}


@api.get(endpoints["settings"])
async def mod_settings():
    # if token:
    #     blablabla
    return config_file.read_settings_file(config_file.abs_file_path)


if config_file.metric_endpoint:

    @api.get(endpoints["metrics"])
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


@api.post(endpoints["thresholds"])
async def mod_settings(
    cpu_percent: float = thresholds["cpu_percent"],
    ram_percent: float = thresholds["ram_percent"],
):
    # if token:
    #     blablabla
    thresholds["cpu_percent"] = cpu_percent
    thresholds["ram_percent"] = ram_percent
    return {"thresholds": thresholds}


@api.on_event("startup")
@repeat_every(seconds=config_file.post_interval, logger=logger, wait_first=True)
def periodic():
    # https://github.com/tiangolo/fastapi/issues/520
    # https://fastapi-utils.davidmontague.xyz/user-guide/repeated-tasks/#the-repeat_every-decorator
    # Changed Timeloop for this
    elapsed_time, data = send_metrics_adapter([static, dynamic])
    send_metrics(
        url=config_file.post_metric_url,
        elapsed_time=elapsed_time,
        data=data,
        file_enabled=config_file.metric_enable_file,
        file_path=config_file.metric_file,
    )
    alert = {}
    if data["cpu_percent"] >= thresholds["cpu_percent"]:
        alert["cpu_percent"] = data["cpu_percent"]
    if data["ram"]["percent"] >= thresholds["ram_percent"]:
        alert["ram_percent"] = data["ram"]["percent"]
    if data["process"]:
        alert["processes"] = data["process"]
    if alert:
        r = requests.post(config_file.alert_url, json={"alert": alert})


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run(
        "monitor_agent.main:api",
        host=config_file.host,
        port=config_file.port,
        reload=config_file.reload,
        workers=config_file.workers,
        log_level=config_file.log_level,
        interface="asgi3",
        debug=config_file.debug,
        backlog=config_file.backlog,
        timeout_keep_alive=config_file.timeout_keep_alive,
        limit_concurrency=config_file.limit_concurrency,
        limit_max_requests=config_file.limit_max_requests,
        ssl_keyfile=config_file.ssl_keyfile,
        ssl_keyfile_password=config_file.ssl_keyfile_password,
        ssl_certfile=config_file.ssl_certfile,
        ssl_version=config_file.ssl_version,
        ssl_cert_reqs=config_file.ssl_cert_reqs,
        ssl_ca_certs=config_file.ssl_ca_certs,
        ssl_ciphers=config_file.ssl_ciphers,
    )
