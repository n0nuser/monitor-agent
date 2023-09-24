from litestar import Router

from monitor_agent.api.endpoints.metrics import metrics_endpoint
from monitor_agent.api.endpoints.settings import mod_settings
from monitor_agent.api.endpoints.thresholds import thresholds


router = Router(path="/", route_handlers=[mod_settings, thresholds, metrics_endpoint])
