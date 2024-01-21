import dataclasses
import datetime
import uuid

@dataclasses.dataclass
class Session:
    id: uuid.UUID
    user_id: int
    valid_to: datetime.datetime
