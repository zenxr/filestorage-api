import dataclasses
from typing import Optional, List

import fastapi

from . import models, schemas
import db

cursor = db.ManagedCursor(models.User)

router = fastapi.APIRouter(
    prefix="/users", tags=["users"], responses={404: {"description": "Not found"}}
)


@router.post("/", response_model=schemas.OutUser)
def create_user(user: schemas.InUser):
    cursor.fetchone(
        "insert into filestorage_user (username, password, email) values (%s, %s, %s)",
        (user.username, user.hash_salt_pass(), user.email),
    )

@router.get("/{user_id}", response_model=schemas.OutUser)
def find_by_id(user_id: int):
    return cursor.fetchone("select * from filestorage_user where id=%s", (user_id,))


@router.put("/", response_model=schemas.OutUser)
def update_user(user: schemas.OutUser):
    return cursor.fetchone(
        (
            "update filestorage_user set username=%{username}, password=${password}"
            ", email=${email}, created_on=${created_on} where id=${id}"
        ),
        dataclasses.asdict(user),
    )


@router.get("/", response_model=List[(schemas.OutUser)])
def find_all(max: Optional[int] = None):
    if max is not None:
        return cursor.fetchmany("select * from filestorage_user", max)
    return cursor.fetchall("select * from filestorage_user")
