import psutil
from monitor_agent.domain.services.os_functions.utils import timestamp_to_isoformat


def boot_date() -> str:
    """Boot date in ISO format 'YYYY-MM-DD HH:MM:SS.mmmmmm'

    Returns:
        str: Boot date.
    """
    return timestamp_to_isoformat(psutil.boot_time())
