from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    username: str
    terminal: Optional[str]
    host: Optional[str]
    started: str
