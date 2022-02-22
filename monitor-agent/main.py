import uvicorn
import logging
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from .settings import settings
from .core.metricFunctions import send_metrics, send_metrics_adapter, static, dynamic
from .core.command import Command

logger = logging.getLogger(__name__)
api = FastAPI()

endpoints = {
    "root": "/",
    "command": "/command",
}


@api.get(endpoints["root"])
async def root():
    return {"message": "Hello World"}


@api.post(endpoints["command"])
async def command(command: str, timeout: int = 10):
    # if token:
    #     blablabla
    return Command(command, timeout).__dict__


@api.on_event("startup")
@repeat_every(seconds=settings.post_task_interval, logger=logger, wait_first=True)
def periodic():
    # https://github.com/tiangolo/fastapi/issues/520
    # https://fastapi-utils.davidmontague.xyz/user-guide/repeated-tasks/#the-repeat_every-decorator
    # Changed Timeloop for this
    elapsed_time, data = send_metrics_adapter([static, dynamic])
    send_metrics(url=settings.metrics_URL, elapsed_time=elapsed_time, data=data)


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run(
        "monitor-agent.main:api",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
