import dataclasses
from typing import Optional, List

import fastapi

from . import models, schemas, service
import db

cursor = db.ManagedCursor(models.User)

router = fastapi.APIRouter(
    prefix="/users", tags=["users"], responses={404: {"description": "Not found"}}
)


@router.post("/", response_model=schemas.OutUser)
def create_user(user: schemas.InUser):
    if cursor.fetchone(
        "select * from filestorage_user where username = %s or email = %s",
        (user.username, user.email),
    ):
        raise fastapi.HTTPException(
            fastapi.status.HTTP_409_CONFLICT, "Username or email already taken"
        )
    created_user = cursor.fetchone(
        "insert into filestorage_user (username, password, email) values (%s, %s, %s) returning * ;",
        (user.username, user.hash_salt_pass(), user.email),
    )
    return schemas.OutUser.from_user(created_user)


@router.get("/{user_id}", response_model=schemas.OutUser)
def find_by_id(user_id: int):
    return cursor.fetchone("select * from filestorage_user where id=%s ;", (user_id,))


# TODO: only admin allowed to do this,
# also missing pw hash
# @router.put("/", response_model=schemas.OutUser)
# def update_user(user: schemas.OutUser):
#     return cursor.fetchone(
#         (
#             "update filestorage_user set username=%{username}, password=${password}"
#             ", email=${email}, created_on=${created_on} where id=${id}"
#         ),
#         dataclasses.asdict(user),
#     )


@router.get("/", response_model=List[(schemas.OutUser)])
def find_all(max: Optional[int] = None):
    service.fetch_users(max=max)
