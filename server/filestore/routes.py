import os
from pathlib import Path

from typing import Annotated

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse

import fastapi

import config
from auth import util as authutil

router = fastapi.APIRouter(
    prefix="/files",
    tags=["buckets"],
    dependencies=[fastapi.Depends(authutil.authorization_required)],
    responses={404: {"description": "Not found"}},
)

# TODO buckets, files
# this is just serving as a how to for now


@router.post("/")
async def create_file(file: fastapi.UploadFile)
async def create_file(file: fastapi.UploadFile):
    # TODO: single or multiple files
    # status endpoints to check progress?
    if not file.filename:
        raise fastapi.HTTPException(status_code=400, detail="Filename not found")
    file_path = Path(config.filestore_path) / file.filename
    with file_path.open("wb") as buffer:
        buffer.write(await file.read())
    return fastapi.responses.Response(f"Uploaded {file}", status_code=201)


@router.put("/{filename:path}")
async def update_file(filename: str, file: fastapi.UploadFile):
    filepath = Path(config.filestore_path) / filename
    if not filepath.is_file():
        raise fastapi.HTTPException(
            status_code=404, detail=f"File not found: {filename}"
        )
    with filepath.open("rb") as buffer:
        buffer.write(await file.read())
    return fastapi.responses.Response(f"Updated {filename}")


@router.get("/files/{filename:path}")
async def read_file(filename: str):
    filepath = Path(config.filestore_path) / filename
    if not filepath.is_file():
        raise fastapi.HTTPException(
            status_code=404, detail=f"File not found: {filename}"
        )
    return fastapi.responses.FileResponse(str(filepath))


@router.delete("/files/{filename:path}")
async def delete_file(filename: str):
    filepath = Path("uploads") / filename
    if not filepath.is_file():
        raise fastapi.HTTPException(
            status_code=404, detail=f"File not found: {filename}"
        )
    os.remove(filepath)
    return fastapi.responses.Response(f"Deleted {filename}")
