import re
import sys
import json
import uvicorn
import logging
import requests
from urllib3.exceptions import MaxRetryError, NewConnectionError
from fastapi import FastAPI, UploadFile, File
from fastapi_utils.tasks import repeat_every
from monitor_agent.core.helper import save2log
from .settings import Settings
from .core.metricFunctions import send_metrics, send_metrics_adapter, static, dynamic
from .core.command import Command

config_file = Settings()

logger = logging.getLogger(__name__)
api = FastAPI()

endpoints = {
    "root": "/",
    "command": "/command",
    "metrics": "/metrics",
    "settings": "/settings",
    "thresholds": "/thresholds",
}

thresholds_dict = {
    "cpu_percent": 50,
    "ram_percent": 30,
}

# GET
@api.get(endpoints["root"])
async def root():
    return {"endpoints": endpoints}


@api.get(endpoints["thresholds"])
async def thresholds():
    return {"thresholds": thresholds_dict}


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
    cpu_percent: float = thresholds_dict["cpu_percent"],
    ram_percent: float = thresholds_dict["ram_percent"],
):
    # if token:
    #     blablabla
    thresholds_dict["cpu_percent"] = cpu_percent
    thresholds_dict["ram_percent"] = ram_percent
    return {"thresholds": thresholds_dict}


@api.on_event("startup")
@repeat_every(seconds=config_file.post_interval, logger=logger, wait_first=True)
def periodic():
    # https://github.com/tiangolo/fastapi/issues/520
    # https://fastapi-utils.davidmontague.xyz/user-guide/repeated-tasks/#the-repeat_every-decorator
    # Changed Timeloop for this
    elapsed_time, data = send_metrics_adapter([static, dynamic])
    try:
        send_metrics(
            url=config_file.post_metric_url,
            elapsed_time=elapsed_time,
            data=data,
            file_enabled=config_file.metric_enable_file,
            file_path=config_file.metric_file,
        )
    except (
        ConnectionRefusedError,
        requests.exceptions.ConnectionError,
        NewConnectionError,
        MaxRetryError,
    ) as msg:
        save2log(
            type="ERROR",
            data=f'Could not connect to "{config_file.post_metric_url}" ({msg})',
        )

    alert = {}
    if data["cpu_percent"] >= thresholds_dict["cpu_percent"]:
        alert["cpu_percent"] = data["cpu_percent"]
    if data["ram"]["percent"] >= thresholds_dict["ram_percent"]:
        alert["ram_percent"] = data["ram"]["percent"]
    try:
        if data["process"]:
            alert["processes"] = data["process"]
    except KeyError as msg:
        pass
    if alert:
        try:
            r = requests.post(config_file.post_alert_url, json={"alert": alert})
        except requests.exceptions.MissingSchema:
            # If invalid URL is provided
            save2log(
                type="ERROR",
                data=f'Invalid POST URL for Alerts ("{config_file.post_alert_url}")',
            )


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
