from typing import Dict
import psutil
import platform

from pydantic import BaseModel

from monitor_agent.domain.entities.network import NetworkInterface
from monitor_agent.domain.services.os_functions.boot_date import (
    boot_date as boot_date_function,
)
from monitor_agent.domain.services.os_functions.network.ip_address import ip_addresses


class StaticMetric(BaseModel):
    """Metrics that never or rarely change."""

    cpu_core_physical: int = psutil.cpu_count(logical=False)
    cpu_core_total: int = psutil.cpu_count(logical=True)
    ip: Dict[str, NetworkInterface] = ip_addresses()
    boot_date: str = boot_date_function()
    host: str = platform.uname().node
    os: str = platform.system()
    os_version: str = platform.version()
    architecture: str = platform.machine()
