from litestar import Litestar

from monitor_agent.api.endpoints import router


app = Litestar(
    route_handlers=[router],
)
