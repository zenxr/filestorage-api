import models
import db

import dataclasses

@dataclasses.dataclass
class UserService:
    def __init__(self):
        self.fetch_one = db.make_fetch_one(models.User)
        self.fetch_many = db.make_fetch_many(models.User)
        self.fetch_all = db.make_fetch_all(models.User)

user_service = UserService()
user_service.fetch_one

user_service2 = db.ManagedCursor(models.User)
