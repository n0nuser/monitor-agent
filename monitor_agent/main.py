import json
from monitor_agent.core.helper import getLogger
import uvicorn
import logging
import requests
from .settings import Settings
from .core.command import Command
from fastapi import FastAPI, UploadFile
from fastapi_utils.tasks import repeat_every


try:
    CONFIG = Settings()
except json.decoder.JSONDecodeError as msg:
    logging.critical(f'Error in "settings.json". {msg}')
    exit()

LOGGER = getLogger(CONFIG)

from .core.metricFunctions import send_metrics, send_metrics_adapter, static, dynamic

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
    return {"thresholds": CONFIG.thresholds.__dict__}


if CONFIG.metrics.get_endpoint:

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
    global CONFIG
    data: str = settings.file.read().decode()
    msg = CONFIG.write_settings(data)
    CONFIG = Settings()
    return msg


@api.on_event("startup")
@repeat_every(seconds=CONFIG.metrics.post_interval, logger=LOGGER, wait_first=True)
def periodic():
    # https://github.com/tiangolo/fastapi/issues/520
    # https://fastapi-utils.davidmontague.xyz/user-guide/repeated-tasks/#the-repeat_every-decorator
    # Changed Timeloop for this
    elapsed_time, data = send_metrics_adapter([static, dynamic])
    send_metrics(
        url=CONFIG.metrics.post_url,
        elapsed_time=elapsed_time,
        data=data,
        file_enabled=CONFIG.metrics.enable_logfile,
        file_path=CONFIG.metrics.log_filename,
    )

    alert = {}
    if data["cpu_percent"] >= CONFIG.thresholds.cpu_percent:
        alert["cpu_percent"] = data["cpu_percent"]
    if data["ram"]["percent"] >= CONFIG.thresholds.ram_percent:
        alert["ram_percent"] = data["ram"]["percent"]
    try:
        if data["process"]:
            alert["processes"] = data["process"]
    except KeyError as msg:
        pass
    if alert:
        r = requests.post(CONFIG.alerts.url, json={"alert": alert})


def start():
    """Launched with `poetry run start` at root level"""
    uviconfig = {"app": "monitor_agent.main:api", "interface": "asgi3"}
    uviconfig.update(CONFIG.uvicorn.__dict__)
    uviconfig.pop("__module__", None)
    uviconfig.pop("__dict__", None)
    uviconfig.pop("__weakref__", None)
    uviconfig.pop("__doc__", None)
    try:
        uvicorn.run(**uviconfig)
    except:
        LOGGER.critical("Unable to run server.", exc_info=True)
