import psutil
import platform
import time
import datetime

from monitor_agent.main import logging


class Status:
    # def __init__(self, error_code, error_message, elapsed):
    def __init__(self, elapsed):
        self.timestamp = datetime.datetime.now().isoformat()
        # self.error_code = error_code
        # self.error_message = error_message
        self.elapsed = elapsed


class MetricStatic:
    def __init__(self):
        self.cpu_core_physical = psutil.cpu_count(logical=False)
        self.cpu_core_total = psutil.cpu_count(logical=True)
        self.disk = _disk_list()
        self.ip = _ip_addresses()
        self.boot_date = _boot_date()
        self.host = platform.uname().node
        self.os = platform.system()
        self.os_version = platform.version()
        self.architecture = platform.machine()


class MetricDynamic:
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
        self.processes = _process(self.ram["total"], self.cpu_percent)
        self.disk_percent = _disk_percent()
        self.uptime = _uptime()


def _format_timestamp(date: float):
    """_summary_

    Args:
        date (float): Date in seconds

    Returns:
        string: Timestamp in ISO format 'YYYY-MM-DD HH:MM:SS.mmmmmm'
    """
    return datetime.datetime.fromtimestamp(date).isoformat()


def _uptime():
    """_summary_

    Returns:
        string: Returns Uptime in format "HH:MM:SS"
    """
    return str(datetime.timedelta(seconds=(time.time() - psutil.boot_time())))


def _cur_network_traffic(interval=1):
    """_summary_

    Args:
        interval (int, optional): Interval to wait for packet frames to be captured. Defaults to 1.

    Returns:
        tuple[str, str]: _description_
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


def _process(ram: int, pc_cpu_percent):
    process = {}
    threshold = 10
    for p in psutil.process_iter(["name", "username"]):
        with p.oneshot():
            cpu_percent = p.cpu_percent()
            ram_percent = round((p.memory_info().vms / ram) * 100, 2)
            if (
                cpu_percent > threshold and not cpu_percent > pc_cpu_percent
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


def _boot_date():
    boot_time_timestamp = psutil.boot_time()
    return _format_timestamp(boot_time_timestamp)


def _ip_addresses():
    addresses = {}
    for key, value in psutil.net_if_addrs().items():
        ifaces = {}
        for interfaces in value:
            ifaces[interfaces.address] = interfaces._asdict()
            ifaces[interfaces.address].pop("address", None)
        addresses[key] = ifaces
    return addresses


def _disk_percent():
    p = psutil.Process()
    io_counters = p.io_counters()
    disk_usage_process = io_counters[2] + io_counters[3]  # read_bytes + write_bytes
    disk_io_counter = psutil.disk_io_counters()
    disk_total = disk_io_counter[2] + disk_io_counter[3]  # read_bytes + write_bytes
    disk = round(disk_usage_process / disk_total * 100, 2)
    return disk


def _disk_list():
    disk_list = {}
    for disk in psutil.disk_partitions(all=False):
        try:
            disk_location = disk.device
            disk_list[disk_location] = psutil.disk_usage(disk_location)._asdict()
        except PermissionError as msg:
            continue
    return disk_list


def _user_list():
    users = {}
    for index, value in enumerate(psutil.users()):
        users[index] = value._asdict()
        users[index]["started"] = _format_timestamp(value._asdict()["started"])
    return users
