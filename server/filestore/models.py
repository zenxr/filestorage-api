import dataclasses
import datetime
from typing import Optional

@dataclasses.dataclass
class Bucket:
    id: int
    name: str
    created_by: int
    created_on: datetime.datetime

@dataclasses.dataclass
class File:
    id: int
    path: str
    bucket_id: int
    created_by: int
    created_on: datetime.datetime
    updated_on: Optional[datetime.datetime] = None

@dataclasses.dataclass
class CreateFile:
    path: str
    bucket_id: int

