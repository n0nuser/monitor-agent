from typing import Dict
import psutil
from monitor_agent.domain.entities.process import ProcessInfo

from monitor_agent.logger import LOGGER


def processes(pc_cpu_percent: float) -> Dict[int, ProcessInfo]:
    """Retrieves processes that exceed a 5% of CPU or RAM usage.

    Args:
        pc_cpu_percent (float): CPU usage percentage of the host.
                                Used to determine if a process has correct CPU usage values.

    Returns:
        dict: Dictionary with processes that exceed 5% of CPU or RAM usage.
              Format is: {pid: {name: str, cpu_percent: float, memory_percent: float, ppid: int}}
    """
    process_list = {}
    threshold = 5
    for p in psutil.process_iter(["name", "username"]):
        with p.oneshot():
            cpu_percent = round(p.cpu_percent(), 2)
            ram_percent = round(p.memory_percent(), 2)

            if (
                cpu_percent > threshold and cpu_percent <= pc_cpu_percent
            ) or ram_percent > threshold:
                process_list[p.pid] = {
                    "name": p.name(),
                    "cpu_percent": cpu_percent,
                    "ram_percent": ram_percent,
                    "ppid": p.ppid(),
                }

                try:
                    # Requires elevated permissions SOMETIMES
                    process_list[p.pid]["username"] = p.username()
                    # Requires elevated permissions
                    process_list[p.pid]["path"] = p.exe()
                except (PermissionError, psutil.AccessDenied):
                    LOGGER.warning(
                        "Could not get Username or Path for process %s", p.name()
                    )
    return process_list
