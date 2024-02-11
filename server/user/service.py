from typing import Optional

from . import models
import db

cursor = db.ManagedCursor(models.User)

def fetch_users(max: Optional[int] = None):
    if max is not None:
        return cursor.fetchmany("select * from filestorage_user", max)
    return cursor.fetchall("select * from filestorage_user")
