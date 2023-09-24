from monitor_agent.domain.services.command import Command
from monitor_agent.logger import get_logger
from fastapi import FastAPI, UploadFile, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi_utils.tasks import repeat_every
from settings import Settings
import contextlib
import json
import logging
import uvicorn


try:
    CONFIG = Settings()
except json.decoder.JSONDecodeError as msg:
    logging.critical(f'Error in "settings.json". {msg}')
    exit()

get_logger(CONFIG.logging.level, CONFIG.logging.filename)

from monitor_agent.domain.metricFunctions import (
    send_metrics,
    send_metrics_adapter,
    static,
    dynamic,
)


def start() -> None:
    """Retrieves the Uvicorn server settings and starts the server."""
    uviconfig = {"app": "main:api", "interface": "asgi3"}
    uviconfig.update(CONFIG.uvicorn.__dict__)
    uviconfig.pop("__module__", None)
    uviconfig.pop("__dict__", None)
    uviconfig.pop("__weakref__", None)
    uviconfig.pop("__doc__", None)
    try:
        uvicorn.run(**uviconfig)
    except Exception:
        logging.critical("Unable to run server.", exc_info=True)


if __name__ == "__main__":
    start()
