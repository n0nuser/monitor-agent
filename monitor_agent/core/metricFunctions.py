import json
import time
import typing
import requests
import logging
from requests.exceptions import ConnectionError, InvalidSchema
from urllib3.exceptions import MaxRetryError, NewConnectionError

from core.models import Status, MetricDynamic, MetricStatic


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
    elapsed_time: dict,
    metrics: dict,
    file_enabled: bool,
    file_path: str,
    metric_endpoint: str,
    agent_endpoint: str,
    user_token: str,
    agent_token: str,
    name: str,
):
    status = Status(elapsed=elapsed_time).__dict__
    if not agent_endpoint.endswith("/"):
        agent_endpoint = agent_endpoint + "/"
    if not metric_endpoint.endswith("/"):
        metric_endpoint = metric_endpoint + "/"

    agent_token = f"{agent_endpoint}{agent_token}/"
    json_request = {
        "agent": agent_token,
        "name": name,
        "metrics": metrics,
        "status": status,
    }
    logging.debug(f"Agent token: {agent_token}")
    logging.debug(f"Metric endpoint: {metric_endpoint}")

    try:
        r = requests.post(
            metric_endpoint,
            json=json_request,
            headers={"Authorization": f"Token {user_token}"},
        )
        logging.debug(f"Response: {r.text}")
        logging.debug(f"Status Code: {r.status_code}")
    except (
        MaxRetryError,
        NewConnectionError,
        ConnectionRefusedError,
        ConnectionError,
        InvalidSchema,
    ) as e:
        logging.critical(
            f"Agent could not send metrics to server {metric_endpoint}", exc_info=True
        )
    if file_enabled:
        with open(file_path, "w") as f:
            f.write(json.dumps(json_request, indent=4, sort_keys=True))
