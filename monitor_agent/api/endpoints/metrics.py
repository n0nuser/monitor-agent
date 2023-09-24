import time
from litestar import get
from monitor_agent.api.schemas.metrics import MetricSchema
from monitor_agent.domain.services.dynamic_metric import DynamicMetric
from monitor_agent.domain.services.static_metric import StaticMetric


@get(path="metrics")
async def metrics_endpoint() -> MetricSchema:
    """Endpoint for getting the metrics.

    Args:
        credentials (HTTPBasicCredentials, optional): Credentials. Defaults to Depends(security).

    Returns:
        dict: Dictionary with the metrics.
    """
    start_time = time.time()
    static = StaticMetric()
    dynamic = DynamicMetric()
    return MetricSchema(
        static_metric=static,
        dynamic_metric=dynamic,
        elapsed_time=time.time() - start_time,
    )
