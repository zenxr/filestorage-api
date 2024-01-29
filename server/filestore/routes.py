import os
import pathlib
import db

from . import models, schemas

from typing import Annotated, Optional

import fastapi

import config
from auth import util as authutil

bucket_cursor = db.ManagedCursor(models.Bucket)
file_cursor = db.ManagedCursor(models.File)

bucket_router = fastapi.APIRouter(
    prefix="/buckets",
    tags=["buckets"],
    dependencies=[fastapi.Depends(authutil.refresh_session)],
    responses={404: {"description": "Not found"}},
)


@bucket_router.post("/")
def create_bucket(
    request: fastapi.Request,
    name: Annotated[str | None, fastapi.Form()] = None,
    bucket: Optional[schemas.CreateBucketRequest] = None,
):
    # ugly, accepting both form data and request params
    if not (_user := authutil.current_user(request)):
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED)

    if bucket:
        name = bucket.name
    elif not name:
        raise fastapi.HTTPException(status_code=400, detail="Name required via param or form data")

    return bucket_cursor.fetchone(
        """
        insert into bucket (name, created_by) values (%s, %s) returning *;
        """,
        (name, _user.id),
    )


@bucket_router.get("/create")
def get_bucket_form():
    # just a silly pass-through
    return fastapi.responses.HTMLResponse(
        """
        <html>
        <body>
        <form action="/buckets/" method="post">
            <input type="text" name="name" id="name" required><br>
            <input type="submit" name="submit" value="submit">
        </form>
        </body>
        </html>
        """
    )


@bucket_router.get("/")
def find_all(max: Optional[int] = None):
    if max is not None:
        return bucket_cursor.fetchmany("select * from bucket", max)
    return bucket_cursor.fetchall("select * from bucket")


@bucket_router.get("/{bucket_id}")
def find_by_name(name: str):
    return bucket_cursor.fetchone("select * from bucket where name = %s", (name,))


router = fastapi.APIRouter(
    prefix="/files",
    tags=["buckets", "files"],
    dependencies=[fastapi.Depends(authutil.refresh_session)],
    responses={404: {"description": "Not found"}},
)


def bucket_by_name(name: str):
    return bucket_cursor.fetchone("select * from bucket where id=%s", (name,))


def create_file(file: models.CreateFile, user_id: int):
    return file_cursor.fetchone(
        "insert into file (path, bucket_id, created_by) values (%s, %s, %s) returning * ;",
        (file.path, file.bucket_id, user_id),
    )


# TODO buckets, files
# this is just serving as a how to for now


@authutil.authorization_required
@router.post("/upload/")
async def upload_file(
    request: fastapi.Request,
    file: Annotated[fastapi.UploadFile, fastapi.File()],
    bucket: Annotated[str, fastapi.Form()],
    path: Annotated[pathlib.Path, fastapi.Form()],
):
    if not file.filename:
        raise fastapi.HTTPException(status_code=400, detail="No filename provided.")
    if not (_bucket := bucket_by_name(bucket)):
        raise fastapi.HTTPException(status_code=400, detail="Invalid bucket name.")
        # TODO: this should be some auto-generated UUID
    if not (_user := authutil.current_user(request)):
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED)
    filepath = pathlib.Path(config.filestore_path) / file.filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with filepath.open("wb") as buffer:
        buffer.write(await file.read())
    _file = models.CreateFile(path=str(filepath), bucket_id=_bucket.id)
    create_file(_file, _user.id)
    return {
        "bucket": bucket,
        "file_content_type": file.content_type,
        "filename": file.filename,
    }


@router.get("/upload")
def get_upload_form():
    content = """
    <html>
    <body>
    <form action="/files/upload/" enctype="multipart/form-data" method="post">
    <label for="file">File:</label><br>
    <input type="file" name="file" id="file" required>
    <br>
    <label for="bucket">Bucket:</label><br>
    <input type="text" id="bucket" name="bucket" required>
    <br>
    <label for="path">Path:</label><br>
    <input type="text" id="path" name="path" required>
    <br>
    <input type="submit">
    </form>
    </body>
    </html>
    """
    return fastapi.responses.HTMLResponse(content=content)

# TODO: DELETE, PUT @ files


# @router.post("/")
# async def create_file(file: fastapi.UploadFile)
# async def create_file(file: fastapi.UploadFile):
#     # TODO: single or multiple files
#     # status endpoints to check progress?
#     if not file.filename:
#         raise fastapi.HTTPException(status_code=400, detail="Filename not found")
#     file_path = Path(config.filestore_path) / file.filename
#     with file_path.open("wb") as buffer:
#         buffer.write(await file.read())
#     return fastapi.responses.Response(f"Uploaded {file}", status_code=201)
#
#
# @router.put("/{filename:path}")
# async def update_file(filename: str, file: fastapi.UploadFile):
#     filepath = Path(config.filestore_path) / filename
#     if not filepath.is_file():
#         raise fastapi.HTTPException(
#             status_code=404, detail=f"File not found: {filename}"
#         )
#     with filepath.open("rb") as buffer:
#         buffer.write(await file.read())
#     return fastapi.responses.Response(f"Updated {filename}")
#
#
# @router.get("/files/{filename:path}")
# async def read_file(filename: str):
#     filepath = Path(config.filestore_path) / filename
#     if not filepath.is_file():
#         raise fastapi.HTTPException(
#             status_code=404, detail=f"File not found: {filename}"
#         )
#     return fastapi.responses.FileResponse(str(filepath))
#
#
# @router.delete("/files/{filename:path}")
# async def delete_file(filename: str):
#     filepath = Path("uploads") / filename
#     if not filepath.is_file():
#         raise fastapi.HTTPException(
#             status_code=404, detail=f"File not found: {filename}"
#         )
#     os.remove(filepath)
#     return fastapi.responses.Response(f"Deleted {filename}")
