# import uvicorn
import requests
import time
import os
from timeloop import Timeloop
from datetime import timedelta

# from fastapi import FastAPI
from core.settings import settings
from core.models.metrics import Status, MetricDynamic, MetricStatic


def execution_time_decorator(function) -> tuple[float, dict]:
    start_time = time.time()
    data = function().__dict__
    end_time = time.time() - start_time
    return round(end_time, 2), data


def static() -> tuple[dict, dict]:
    static_time, static_data = execution_time_decorator(MetricStatic)
    return {"static": static_time}, static_data


def dynamic() -> tuple[dict, dict]:
    dynamic_time, dynamic_data = execution_time_decorator(MetricDynamic)
    return {"dynamic": dynamic_time}, dynamic_data


def make_request_adapter(function_list: list) -> tuple[dict, dict]:
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
    print(r.json())


#######################################

# app = FastAPI()

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}

# def start():
#     """Launched with `poetry run start` at root level"""
#     uvicorn.run("monitor-agent.main:app", host=settings.host, port=settings.port, reload=settings.reload)

if __name__ == "__main__":
    # Ref: https://medium.com/greedygame-engineering/an-elegant-way-to-run-periodic-tasks-in-python-61b7c477b679
    # tl = Timeloop()

    # @tl.job(interval=timedelta(seconds=settings.post_task_interval))
    # def make_request_task():
    #     elapsed_time, data = make_request_adapter([static, dynamic])
    #     make_request(elapsed_time=elapsed_time, data=data)

    # tl.start(block=True)

    elapsed_time, data = make_request_adapter([static, dynamic])
    make_request(elapsed_time=elapsed_time, data=data)
