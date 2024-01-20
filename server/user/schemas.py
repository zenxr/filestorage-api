import dataclasses
import datetime

import bcrypt


@dataclasses.dataclass
class InUser:
    username: str
    password: str
    email: str

    # TODO move me
    def hash_salt_pass(self):
        return bcrypt.hashpw(self.password.encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        )


@dataclasses.dataclass
class OutUser:
    id: int
    username: str
    email: str
    created_on: datetime.datetime
