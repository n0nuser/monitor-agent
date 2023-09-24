from pydantic import BaseModel
from monitor_agent.domain.services.dynamic_metric import DynamicMetric
from monitor_agent.domain.services.static_metric import StaticMetric


class MetricSchema(BaseModel):
    static_metric: StaticMetric
    dynamic_metric: DynamicMetric
    elapsed_time: float
