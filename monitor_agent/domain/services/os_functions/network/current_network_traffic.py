import time
from typing import Tuple

import psutil


def current_network_traffic(interval=1) -> Tuple[int, int]:
    """Returns Actual Network traffic whithin an specified interval.

    Args:
        interval (int, optional): Interval to wait for packet frames to be captured. Defaults to 1.

    Returns:
        Tuple[int, int]: Current Incoming and Outgoing Network traffic in bytes
    """
    # Get net in/out
    net1_out = psutil.net_io_counters().bytes_sent
    net1_in = psutil.net_io_counters().bytes_recv

    time.sleep(interval)

    # Get new net in/out
    net2_out = psutil.net_io_counters().bytes_sent
    net2_in = psutil.net_io_counters().bytes_recv

    # Compare and get current speed
    current_in = 0 if net1_in > net2_in else net2_in - net1_in
    current_out = 0 if net1_out > net2_out else net2_out - net1_out

    return current_in, current_out
