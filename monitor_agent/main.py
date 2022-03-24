import sys
import json
import uvicorn
import logging
import requests
from fastapi import FastAPI, UploadFile
from fastapi_utils.tasks import repeat_every
from .settings import Settings
from .core.metricFunctions import send_metrics, send_metrics_adapter, static, dynamic
from .core.command import Command

try:
    config = Settings()
    print(dir(config))
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

# GET
@api.get(endpoints["root"])
async def root():
    return {"endpoints": endpoints}


@api.get(endpoints["thresholds"])
async def thresholds():
    return {"thresholds": config.thresholds.__dict__}


if config.metrics.get_endpoint:
    @api.get(endpoints["metrics"])
    async def metrics_endpoint():
        elapsed_time, data = send_metrics_adapter([static, dynamic])
        return {"data": data, "elapsed_time": elapsed_time}


# POST
@api.post(endpoints["command"])
async def command(command: str, timeout: int):
    return Command(command, timeout).__dict__


@api.post(endpoints["settings"])
async def mod_settings(settings: UploadFile):
    data: str = settings.file.read().decode()
    return config.write_settings(data)


@api.post(endpoints["thresholds"])
async def mod_settings(cpu_percent: float, ram_percent: float):
    thresholds["cpu_percent"] = cpu_percent
    thresholds["ram_percent"] = ram_percent
    return {"thresholds": thresholds}


@api.on_event("startup")
@repeat_every(seconds=config.metrics.post_interval, logger=logger, wait_first=True)
def periodic():
    # https://github.com/tiangolo/fastapi/issues/520
    # https://fastapi-utils.davidmontague.xyz/user-guide/repeated-tasks/#the-repeat_every-decorator
    # Changed Timeloop for this
    elapsed_time, data = send_metrics_adapter([static, dynamic])
    send_metrics(
        url=config.metrics.post_url,
        elapsed_time=elapsed_time,
        data=data,
        file_enabled=config.metrics.enable_logfile,
        file_path=config.metrics.log_filename,
    )
    alert = {}
    if data["cpu_percent"] >= thresholds["cpu_percent"]:
        alert["cpu_percent"] = data["cpu_percent"]
    if data["ram"]["percent"] >= thresholds["ram_percent"]:
        alert["ram_percent"] = data["ram"]["percent"]
    if data["process"]:
        alert["processes"] = data["process"]
    if alert:
        r = requests.post(config.alerts.url, json={"alert": alert})


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run(
        "monitor_agent.main:api",
        host=config.uvicorn.host,
        port=config.uvicorn.port,
        reload=config.uvicorn.reload,
        workers=config.uvicorn.workers,
        log_level=config.uvicorn.log_level,
        interface="asgi3",
        debug=config.uvicorn.debug,
        backlog=config.uvicorn.backlog,
        timeout_keep_alive=config.uvicorn.timeout_keep_alive,
        limit_concurrency=config.uvicorn.limit_concurrency,
        limit_max_requests=config.uvicorn.limit_max_requests,
        ssl_keyfile=config.uvicorn.ssl_keyfile,
        ssl_keyfile_password=config.uvicorn.ssl_keyfile_password,
        ssl_certfile=config.uvicorn.ssl_certfile,
        ssl_version=config.uvicorn.ssl_version,
        ssl_cert_reqs=config.uvicorn.ssl_cert_reqs,
        ssl_ca_certs=config.uvicorn.ssl_ca_certs,
        ssl_ciphers=config.uvicorn.ssl_ciphers,
    )
