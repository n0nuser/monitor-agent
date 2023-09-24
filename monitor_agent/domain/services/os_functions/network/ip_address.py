from typing import Dict

import psutil

from monitor_agent.domain.entities.network import NetworkInterface


def ip_addresses() -> Dict[str, NetworkInterface]:
    """IP addresses of the host.

    Returns:
        Dict[str, NetworkInterface]: IP addresses of the host.
    """
    interfaces = {}
    for interface_name, addresses_info in psutil.net_if_addrs().items():
        network_interface = NetworkInterface(name=interface_name)
        for addr in addresses_info:
            network_interface.add_ip_address(
                addr.address, addr.family, addr.netmask, addr.broadcast, addr.ptp
            )
        interfaces |= network_interface.model_dump()
    return interfaces
