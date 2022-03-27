import time
import json
import typing
import requests
import logging

from monitor_agent.core.models import Status, MetricDynamic, MetricStatic


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
            logging.warning(f"TypeError: {msg}", exc_info=True)
            continue
    return elapsed_time, data


def send_metrics(
    url: str, elapsed_time: dict, data: dict, file_enabled: bool, file_path: str, auth: dict, port:int
):
    auth.update({"port": port})
    auth.pop("__module__", None)
    auth.pop("__dict__", None)
    auth.pop("__weakref__", None)
    auth.pop("__doc__", None)
    status = Status(elapsed=elapsed_time).__dict__
    json_request = {"auth": auth, "data": data, "status": status}
    try:
        r = requests.post(url, json=json_request, headers={'Authorization': auth["api_token"]})
    except requests.exceptions.InvalidSchema as e:
        logging.critical(f"Agent could not send metrics to server {url}", exc_info=True)
    logging.debug(f"Response: {r.text}")
    logging.debug(f"Status Code: {r.status_code}")
    if file_enabled:
        with open(file_path, "w") as f:
            f.write(json.dumps(json_request, indent=4, sort_keys=True))
