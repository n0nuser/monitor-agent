from typing import Tuple

import psutil


def total_network_traffic() -> Tuple[int, int]:
    """Returns the total network traffic since boot.

    Returns:
        Tuple[int, int]: Total Incoming and Outgoing Network traffic in bytes.
    """
    # get IO statistics since boot
    net_io = psutil.net_io_counters()
    return net_io.bytes_recv, net_io.bytes_sent
