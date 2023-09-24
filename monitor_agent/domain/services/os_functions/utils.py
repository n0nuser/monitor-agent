import datetime
import time


def timestamp_to_isoformat(date: float) -> str:
    """Formats a timestamp to a ISO 8601 string.

    Args:
        date (float): Date in seconds (timestamp)

    Returns:
        str: Timestamp in ISO format 'YYYY-MM-DD HH:MM:SS.mmmmmm'
    """
    return datetime.datetime.fromtimestamp(date).isoformat()


def execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        return elapsed_time, result

    return wrapper
