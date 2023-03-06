from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class User(BaseModel):
    userName: str
    password: str
    # md5: str | None                    # only available after Python 3.10
    md5: Optional[str]
    # lastRefreshTime: datetime | None  # only available after Python 3.10
    lastRefreshTime: Optional[datetime]
