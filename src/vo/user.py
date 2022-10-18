from pydantic import BaseModel
from datetime import datetime


class User(BaseModel):
    userName: str
    password: str
    md5: str | None
    lastRefreshTime: datetime | None
