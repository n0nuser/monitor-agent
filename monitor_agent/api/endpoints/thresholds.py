from litestar import get
from monitor_agent.settings import ThresholdsConfig, get_settings


@get(path="thresholds")
async def thresholds() -> ThresholdsConfig:
    """Endpoint for getting the thresholds.

    Returns:
        ThresholdsConfig: Thresholds.
    """
    return get_settings().thresholds
