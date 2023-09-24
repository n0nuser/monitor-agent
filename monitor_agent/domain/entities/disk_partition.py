from pydantic import BaseModel


class DiskPartition(BaseModel):
    device: str
    fstype: str
    mountpoint: str
    opts: str
    total: int
    used: int
    free: int
    percent: float
