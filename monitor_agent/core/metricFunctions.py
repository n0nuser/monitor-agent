import time
import json
import typing
import requests

from monitor_agent.core.helper import save2log
from .models.metricModel import Status, MetricDynamic, MetricStatic

# Typing Tuple is used to overcome Python ^3.6 until Python 3.10 problem
# with Tuples not being a standard type


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


def send_metrics_adapter(function_list: list) -> typing.Tuple[dict, dict]:
    elapsed_time = {}
    data = {}
    for function in function_list:
        try:
            f_time, f_data = function()
            elapsed_time.update(f_time)
            data.update(f_data)
        except TypeError as msg:
            save2log(type="WARNING", data=f"TypeError: {msg}")
            continue
    return elapsed_time, data


def send_metrics(
    url: str, elapsed_time: dict, data: dict, file_enabled: bool, file_path: str
):
    status = Status(elapsed=elapsed_time).__dict__
    json_request = {"data": data, "status": status}
    r = requests.post(url, json=json_request)
    # DEBUG
    print(r.status_code)
    if file_enabled:
        with open(file_path, "w") as f:
            f.write(json.dumps(json_request, indent=4, sort_keys=True))
