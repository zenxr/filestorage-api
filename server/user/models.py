import dataclasses
import datetime
import bcrypt

@dataclasses.dataclass
class User:
    id: int
    username: str
    password: str
    email: str
    created_on: datetime.datetime

    # TODO: move me
    def check_password(self, plaintext_password: str):
        return bcrypt.checkpw(
            plaintext_password.encode("utf-8"), self.password.encode("utf-8")
        )
