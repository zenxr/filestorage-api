import dataclasses
import datetime

@dataclasses.dataclass
class Session:
    id: str
    user_id: int
    valid_to: datetime.datetime
