import os
from typing import Dict
import psutil

from monitor_agent.domain.entities.disk_partition import DiskPartition


def disks_info() -> Dict[str, DiskPartition]:
    """Retrieve information about disk partitions on the host.

    Returns:
        dict[str, DiskPartition]: A dictionary mapping device names to DiskPartition objects,
            representing information about disk partitions on the host.
    """
    disk_list = {}
    for part in psutil.disk_partitions(all=False):
        if os.name == "nt" and ("cdrom" in part.opts or part.fstype == ""):
            # Skip CD-ROM drives with no disk in it; they may raise
            # ENOENT, pop-up a Windows GUI error for a non-ready
            # partition or just hang.
            continue
        if "loop" in part.device:
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            partition = DiskPartition(
                device=part.device,
                fstype=part.fstype,
                mountpoint=part.mountpoint,
                opts=part.opts,
                total=usage.total,
                used=usage.used,
                free=usage.free,
                percent=usage.percent,
            )
            disk_list[part.device] = partition
        except PermissionError:
            continue
    return disk_list
