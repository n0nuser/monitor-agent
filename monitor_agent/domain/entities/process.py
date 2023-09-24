from typing import Optional

from pydantic import BaseModel


class ProcessInfo(BaseModel):
    name: str
    cpu_percent: float
    ram_percent: float
    ppid: int
    username: Optional[str] = None
    path: Optional[str] = None
