import os
from pathlib import Path

from fastapi import FastAPI, UploadFile
from fastapi import responses
from starlette.exceptions import HTTPException

import config

app = FastAPI()
conf = config.get()


@app.get("/")
async def root():
    return responses.JSONResponse({"app_name": conf.app_name})


@app.get("/ping")
async def info():
    return responses.Response("pong")


@app.post("/files/")
async def create_file(file: UploadFile):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename not found")
    file_path = Path(conf.filestore_path) / file.filename
    with file_path.open("wb") as buffer:
        buffer.write(await file.read())
    return responses.Response(f"Uploaded {file}", status_code=201)


@app.put("/files/{filename:path}")
async def update_file(filename: str, file: UploadFile):
    filepath = Path(conf.filestore_path) / filename
    if not filepath.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    with filepath.open("rb") as buffer:
        buffer.write(await file.read())
    return responses.Response(f"Updated {filename}")


@app.get("/files/{filename:path}")
async def read_file(filename: str):
    filepath = Path(conf.filestore_path) / filename
    if not filepath.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    return responses.FileResponse(str(filepath))


@app.delete("/files/{filename:path}")
async def delete_file(filename: str):
    filepath = Path("uploads") / filename
    if not filepath.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    os.remove(filepath)
    return responses.Response(f"Deleted {filename}")
