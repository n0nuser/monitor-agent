import datetime


class Status:
    """Stores the timestamp and the elapsed time"""

    def __init__(self, elapsed):
        self.timestamp = datetime.datetime.now().isoformat()
        self.elapsed = elapsed
