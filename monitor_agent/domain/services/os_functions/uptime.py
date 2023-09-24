import datetime
import time

import psutil


def uptime() -> str:
    """Returns Uptime in format "HH:MM:SS"

    Returns:
        str: Uptime
    """
    uptime_in_seconds: float = time.time() - psutil.boot_time()
    return str(datetime.timedelta(seconds=uptime_in_seconds))
