from requests.exceptions import ConnectionError, InvalidSchema
from urllib3.exceptions import MaxRetryError, NewConnectionError
import json
import logging
import requests
import time
import typing

from core.models import Status, MetricDynamic, MetricStatic


def execution_time_decorator(function) -> typing.Tuple[float, dict]:
    """Get the execution time of a function.

    Args:
        function (function): Function to time.

    Returns:
        typing.Tuple[float, dict]: Time as float and result of funciton as dict.
    """
    start_time = time.time()
    data = function().__dict__
    end_time = time.time() - start_time
    return round(end_time, 2), data


def static() -> typing.Tuple[dict, dict]:
    """Function to get the static metrics.

    Returns:
        typing.Tuple[dict, dict]: {"static": static_time}; and "static_data" as a dict.
    """
    static_time, static_data = execution_time_decorator(MetricStatic)
    return {"static": static_time}, static_data


def dynamic() -> typing.Tuple[dict, dict]:
    """Function to get the dynamic metrics.

    Returns:
        typing.Tuple[dict, dict]: {"dynamic": dynamic_time}; and "dynamic_data" as a dict.
    """
    dynamic_time, dynamic_data = execution_time_decorator(MetricDynamic)
    return {"dynamic": dynamic_time}, dynamic_data


def send_metrics_adapter(function_list: list) -> typing.Tuple[dict, dict]:
    """Given a list of functions, it executes them and returns the execution time and the result.

    Args:
        function_list (list): List of functions to execute.

    Returns:
        typing.Tuple[dict, dict]: elapsed time and result of the functions.
    """
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
) -> None:
    """Sends metrics to a given endpoint.

    Args:
        elapsed_time (dict): Elapsed time of the functions.
        metrics (dict): Metrics of the host to send.
        file_enabled (bool): If the metrics should be saved to a file.
        file_path (str): Path to the file to save the metrics.
        metric_endpoint (str): Endpoint where the metrics are sent.
        agent_endpoint (str): Endpoint of the agents.
        user_token (str): User token for authentication.
        agent_token (str): Token of the agent.
        name (str): Name of the host.
    """
    status = Status(elapsed=elapsed_time).__dict__

    if not agent_endpoint.endswith("/"):
        agent_endpoint += "/"
    if not metric_endpoint.endswith("/"):
        metric_endpoint += "/"
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
        logging.debug(f"Metric Response: {r.text}")
        logging.debug(f"Metric Status Code: {r.status_code}")
    except (MaxRetryError, NewConnectionError, ConnectionError, InvalidSchema):
        logging.critical(
            f"Agent could not send metrics to server {metric_endpoint}", exc_info=True
        )

    if file_enabled:
        with open(file_path, "w") as f:
            f.write(json.dumps(json_request, indent=4, sort_keys=True))
