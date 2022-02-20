import requests
import uvicorn
import logging
import time
import json
import os
import typing
from datetime import timedelta
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from .core.settings import settings
from .core.models.metrics import Status, MetricDynamic, MetricStatic


logger = logging.getLogger(__name__)
api = FastAPI()


def execution_time_decorator(function) -> typing.Tuple[float, dict]:
    start_time = time.time()
    data = function().__dict__
    end_time = time.time() - start_time
    return round(end_time, 2), data


def static() -> typing.Tuple[dict, dict]:
    static_time, static_data = execution_time_decorator(MetricStatic)
    return {"static": static_time}, static_data


def dynamic() -> typing.Tuple[dict, dict]:
    dynamic_time, dynamic_data = execution_time_decorator(MetricDynamic)
    return {"dynamic": dynamic_time}, dynamic_data


def make_request_adapter(function_list: list) -> typing.Tuple[dict, dict]:
    elapsed_time = {}
    data = {}
    for function in function_list:
        try:
            f_time, f_data = function()
            elapsed_time.update(f_time)
            data.update(f_data)
        except TypeError as msg:
            print(msg)
            continue
    return elapsed_time, data


def make_request(elapsed_time: dict, data: dict):
    status = Status(elapsed=elapsed_time).__dict__
    json_request = {"data": data, "status": status}
    r = requests.post(settings.metrics_URL, json=json_request)
    # DEBUG
    # print(r.status_code)
    # with open(settings.metrics_file, "w") as f:
    #     f.write(json.dumps(json_request, indent=4, sort_keys=True))


@api.get("/")
async def root():
    return {"message": "Hello World"}


@api.on_event("startup")
@repeat_every(seconds=settings.post_task_interval, logger=logger, wait_first=True)
def periodic():
    # https://github.com/tiangolo/fastapi/issues/520
    # https://fastapi-utils.davidmontague.xyz/user-guide/repeated-tasks/#the-repeat_every-decorator
    # Changed Timeloop for this
    elapsed_time, data = make_request_adapter([static, dynamic])
    make_request(elapsed_time=elapsed_time, data=data)


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run(
        "monitor-agent.main:api",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
