import psutil
import platform
import time
import datetime
import asyncio


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
        self.ram = _ram_data()
        self.network_current_in, self.network_current_out = asyncio.run(
            _cur_network_traffic()
        )
        self.network_total_in, self.network_total_out = _total_network_traffic()
        # self.connections = {}
        # for index, connection in enumerate(psutil.net_connections()):
        #     self.connections[index] = connection
        try:
            self.battery = psutil.sensors_battery()._asdict()
        except AttributeError:
            # If no battery is installed or metrics can’t be determined None is returned.
            self.battery = None
        self.users = _user_list()
        # self.process = {p.pid: p.info for p in psutil.process_iter(['name', 'username'])}
        self.disk_percent = _disk_percent()
        self.uptime = _uptime()


def _get_size(bytes: int, suffix="B"):
    """Scale bytes to its proper format.
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'

    Args:
        bytes (int): Numeric size to format
        suffix (str): Format of introduced size: 'B', 'K', 'M', 'G', 'T', 'P'

    Returns:
        string: Formatted size

    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


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


async def _cur_network_traffic(interval=1):
    """_summary_

    Args:
        interval (int, optional): Interval to wait for packet frames to be captured. Defaults to 1.

    Returns:
        tuple[str, str]: _description_
    """
    # Get net in/out
    net1_out = psutil.net_io_counters().bytes_sent
    net1_in = psutil.net_io_counters().bytes_recv

    await asyncio.sleep(interval)

    # Get new net in/out
    net2_out = psutil.net_io_counters().bytes_sent
    net2_in = psutil.net_io_counters().bytes_recv

    # Compare and get current speed
    current_in = 0 if net1_in > net2_in else net2_in - net1_in
    current_out = 0 if net1_out > net2_out else net2_out - net1_out

    # Final Variables
    # Traffic in Megabytes
    network_current_in = _get_size(round(current_in, 2))
    network_current_out = _get_size(round(current_out, 2))

    return network_current_in, network_current_out


def _total_network_traffic():
    # get IO statistics since boot
    net_io = psutil.net_io_counters()
    network_total_out = _get_size(net_io.bytes_sent)
    network_total_in = _get_size(net_io.bytes_recv)
    return network_total_in, network_total_out


def _boot_date():
    boot_time_timestamp = psutil.boot_time()
    return _format_timestamp(boot_time_timestamp)


def _ram_data():
    ram = psutil.virtual_memory()._asdict()
    for key, value in ram.items():
        if key != "percent":
            ram[key] = _get_size(value)
    return ram


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
            disk_list[disk_location]["free"] = _get_size(
                disk_list[disk_location]["free"]
            )
            disk_list[disk_location]["total"] = _get_size(
                disk_list[disk_location]["total"]
            )
            disk_list[disk_location]["used"] = _get_size(
                disk_list[disk_location]["used"]
            )
        except PermissionError as msg:
            continue
    return disk_list


def _user_list():
    users = {}
    for index, value in enumerate(psutil.users()):
        users[index] = value._asdict()
        users[index]["started"] = _format_timestamp(value._asdict()["started"])
    return users
