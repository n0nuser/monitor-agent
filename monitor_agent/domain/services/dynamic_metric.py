from typing import Dict, List, Union
import psutil
from pydantic import BaseModel

from monitor_agent.domain.entities.disk_partition import DiskPartition
from monitor_agent.domain.entities.process import ProcessInfo
from monitor_agent.domain.entities.user import User
from monitor_agent.domain.services.os_functions.disk_info import disks_info
from monitor_agent.domain.services.os_functions.logged_users import logged_users
from monitor_agent.domain.services.os_functions.network.current_network_traffic import (
    current_network_traffic,
)
from monitor_agent.domain.services.os_functions.network.total_network_traffic import (
    total_network_traffic,
)
from monitor_agent.domain.services.os_functions.processes import processes
from monitor_agent.domain.services.os_functions.uptime import uptime


class DynamicMetric(BaseModel):
    cpu_freq: dict
    cpu_percent: float
    ram: dict
    network_current_in: int
    network_current_out: int
    network_total_in: int
    network_total_out: int
    battery: Union[None, dict]
    users: List[User]
    processes: Dict[int, ProcessInfo]
    disk: Dict[str, DiskPartition]
    uptime: str

    def __init__(self):
        self.cpu_freq = psutil.cpu_freq()._asdict()
        self.cpu_percent = psutil.cpu_percent()
        self.ram = psutil.virtual_memory()._asdict()
        self.network_current_in, self.network_current_out = current_network_traffic()
        self.network_total_in, self.network_total_out = total_network_traffic()
        try:
            self.battery = psutil.sensors_battery()._asdict()
        except AttributeError:
            # If no battery is installed or metrics can’t be determined, None is returned.
            self.battery = None
        self.users = logged_users()
        self.processes = processes(self.cpu_percent)
        self.disk = disks_info()
        self.uptime = uptime()
        super().__init__()  # Validate the model
