from __future__ import annotations

import dataclasses
import datetime

@dataclasses.dataclass
class User:
    id: int
    username: str
    password: str
    email: str
    created_on: datetime.datetime

@dataclasses.dataclass
class CreateUserRequest:
    username: str
    password: str
    email: str

    # Thinking of how to implement this...
    #
    # I want these to simply remain as dataclasses. Consuming services and etc can build the row_factory themselves.
    # @staticmethod
    # def row_factory(cursor: psycopg.Cursor[User]):
    #     return row_factory(User)(cursor)
    #
