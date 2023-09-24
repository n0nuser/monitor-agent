@api.on_event("startup")
@repeat_every(seconds=CONFIG.metrics.post_interval, logger=logging, wait_first=True)
def periodic() -> None:
    """Sends metrics to the server at a given interval. Also sends alerts in case the thresholds are exceeded."""
    # https://github.com/tiangolo/fastapi/issues/520
    # https://fastapi-utils.davidmontague.xyz/user-guide/repeated-tasks/#the-repeat_every-decorator
    # Changed Timeloop for this
    elapsed_time, metrics = send_metrics_adapter([static, dynamic])
    send_metrics(
        elapsed_time=elapsed_time,
        metrics=metrics,
        file_enabled=CONFIG.metrics.enable_logfile,
        file_path=CONFIG.metrics.log_filename,
        metric_endpoint=CONFIG.endpoints.metric_endpoint,
        agent_endpoint=CONFIG.endpoints.agent_endpoint,
        agent_token=CONFIG.auth.agent_token,
        user_token=CONFIG.auth.user_token,
        name=CONFIG.auth.name,
    )

    alert = {
        "cpu_percent": metrics["cpu_percent"],
        "ram_percent": metrics["ram"]["percent"],
    }

    with contextlib.suppress(KeyError):
        if metrics.get("processes", None):
            alert["processes"] = metrics["processes"]

    if (
        metrics.get("cpu_percent", 0) >= CONFIG.thresholds.cpu_percent
        or metrics.get("ram", {}).get("percent", 0) >= CONFIG.thresholds.ram_percent
    ):
        try:
            agent_endpoint = CONFIG.endpoints.agent_endpoint
            agent_token = CONFIG.auth.agent_token
            agent_token = f"{agent_endpoint}{agent_token}/"
            alert["agent"] = agent_token
            r = requests.post(
                CONFIG.alerts.url,
                json=alert,
                headers={"Authorization": f"Token {CONFIG.auth.user_token}"},
            )
            logging.debug(f"Alert Response: {r.text}")
            logging.debug(f"Alert Status Code: {r.status_code}")
        except requests.exceptions.InvalidSchema:
            logging.error(
                f"Agent could not send an alert to {CONFIG.alerts.url}", exc_info=True
            )
