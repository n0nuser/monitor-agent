import os
import psutil
import platform
import time
import datetime
import logging


class Status:
    """Stores the timestamp and the elapsed time"""

    def __init__(self, elapsed):
        self.timestamp = datetime.datetime.now().isoformat()
        self.elapsed = elapsed


class MetricStatic:
    """Metrics that never or rarely change."""

    def __init__(self):
        self.cpu_core_physical = psutil.cpu_count(logical=False)
        self.cpu_core_total = psutil.cpu_count(logical=True)
        self.ip = _ip_addresses()
        self.boot_date = _boot_date()
        self.host = platform.uname().node
        self.os = platform.system()
        self.os_version = platform.version()
        self.architecture = platform.machine()


class MetricDynamic:
    """Metrics that are in constant change."""

    def __init__(self):
        self.cpu_freq = psutil.cpu_freq()._asdict()
        self.cpu_percent = psutil.cpu_percent()
        self.ram = psutil.virtual_memory()._asdict()
        self.network_current_in, self.network_current_out = _cur_network_traffic()
        self.network_total_in, self.network_total_out = _total_network_traffic()
        try:
            self.battery = psutil.sensors_battery()._asdict()
        except AttributeError:
            # If no battery is installed or metrics can’t be determined None is returned.
            self.battery = None
        self.users = _user_list()
        self.processes = _process(self.cpu_percent)
        self.disk = _disk()
        self.uptime = _uptime()


def _format_timestamp(date: float):
    """Format a datetime object to a ISO 8601 string.

    Args:
        date (float): Date in seconds

    Returns:
        str: Timestamp in ISO format 'YYYY-MM-DD HH:MM:SS.mmmmmm'
    """
    return datetime.datetime.fromtimestamp(date).isoformat()


def _uptime():
    """Returns Uptime in format "HH:MM:SS"

    Returns:
        str: Uptime
    """
    uptime_in_seconds: float = time.time() - psutil.boot_time()
    return str(datetime.timedelta(seconds=uptime_in_seconds))


def _cur_network_traffic(interval=1):
    """Returns Actual Network traffic whithin an specified interval.

    Args:
        interval (int, optional): Interval to wait for packet frames to be captured. Defaults to 1.

    Returns:
        tuple[str, str]: Current Incoming and Outgoing Network traffic in bytes
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


def _process(pc_cpu_percent: float) -> dict:
    """Retrieves processes that exceed a 5% of CPU or RAM usage.

    Args:
        pc_cpu_percent (float): CPU usage percentage of the host.
                                Used to determine if a process has correct CPU usage values.

    Returns:
        dict: Dictionary with processes that exceed 5% of CPU or RAM usage.
              Format is: {pid: {name: str, cpu_percent: float, memory_percent: float, ppid: int}}
    """
    process = {}
    threshold = 5
    for p in psutil.process_iter(["name", "username"]):
        with p.oneshot():
            cpu_percent = round(p.cpu_percent(), 2)
            ram_percent = round(p.memory_percent(), 2)

            if (
                cpu_percent > threshold and cpu_percent <= pc_cpu_percent
            ) or ram_percent > threshold:
                process[p.pid] = {
                    "name": p.name(),
                    "cpu_percent": cpu_percent,
                    "ram_percent": ram_percent,
                    "ppid": p.ppid(),
                }

                try:
                    # Requires elevated permissions SOMETIMES
                    process[p.pid]["username"] = p.username()
                    # Requires elevated permissions
                    process[p.pid]["path"] = p.exe()
                except (PermissionError, psutil.AccessDenied):
                    logging.warning(
                        f"Could not get Username or Path for process {p.name()}"
                    )
    return process


def _total_network_traffic():
    # get IO statistics since boot
    net_io = psutil.net_io_counters()
    return net_io.bytes_recv, net_io.bytes_sent


def _boot_date() -> str:
    """Boot date in ISO format 'YYYY-MM-DD HH:MM:SS.mmmmmm'

    Returns:
        str: Boot date.
    """
    return _format_timestamp(psutil.boot_time())


def _ip_addresses() -> dict:
    """IP addresses of the host.

    Returns:
        dict: IP addresses of the host.
    """
    addresses = {}
    for key, value in psutil.net_if_addrs().items():
        ifaces = {}
        for interfaces in value:
            ifaces[interfaces.address] = interfaces._asdict()
            ifaces[interfaces.address].pop("address", None)
        addresses[key] = ifaces
    return addresses


def _disk() -> dict:
    """Disks of the host with its partitions.

    Returns:
        dict: Disks of the host with its partitions.
    """
    disk_list = {}
    for part in psutil.disk_partitions(all=False):
        if os.name == "nt" and ("cdrom" in part.opts or part.fstype == ""):
            # skip cd-rom drives with no disk in it; they may raise
            # ENOENT, pop-up a Windows GUI error for a non-ready
            # partition or just hang.
            continue
        if "loop" in part.device:
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            data: dict = usage._asdict()
            data.update(part._asdict())
            data.pop("device", None)
            disk_list[part.device] = data
        except PermissionError:
            continue
    return disk_list


def _user_list() -> dict:
    """List of logged users.

    Returns:
        dict: List of logged users.
    """
    users = {}
    for index, value in enumerate(psutil.users()):
        users[index] = value._asdict()
        users[index]["started"] = _format_timestamp(value._asdict().get("started", ""))
    return users
