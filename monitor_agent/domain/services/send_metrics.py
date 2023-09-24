from pathlib import Path
import httpx
import json

from monitor_agent.domain.services.status import Status
from monitor_agent.logger import LOGGER


async def send_metrics(
    elapsed_time: float,
    metrics: dict,
    file_enabled: bool,
    file_path: Path,
    metric_endpoint: str,
    agent_endpoint: str,
    user_token: str,
    agent_token: str,
    name: str,
) -> None:
    """Sends metrics to a given endpoint.

    Args:
        elapsed_time (float): Elapsed time of the functions.
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

    LOGGER.debug("Agent token: %s", agent_token)
    LOGGER.debug("Metric endpoint: %s", metric_endpoint)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                metric_endpoint,
                json=json_request,
                headers={"Authorization": f"Token {user_token}"},
            )
            LOGGER.debug("Metric Response: %s", response.json())
            LOGGER.debug("Metric Status Code: %s", response.status_code)
        except httpx.HTTPError:
            LOGGER.critical(
                "Agent could not send metrics to server %s",
                metric_endpoint,
                exc_info=True,
            )

    if file_enabled:
        with open(file_path, "w+", encoding="UTF-8") as f:
            f.write(json.dumps(json_request, indent=4, sort_keys=True))
