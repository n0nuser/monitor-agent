from pydantic import BaseModel
from typing import Dict, Optional


class IPAddress(BaseModel):
    address: str
    family: int
    netmask: Optional[str]
    broadcast: Optional[str]
    ptp: Optional[str]


class NetworkInterface(BaseModel):
    name: str
    ip_addresses: Dict[str, IPAddress] = {}

    def add_ip_address(self, address, family, netmask, broadcast, ptp):
        ip_address = IPAddress(
            address=str(address),
            family=family,
            netmask=netmask,
            broadcast=broadcast,
            ptp=ptp,
        )
        self.ip_addresses[str(address)] = ip_address
