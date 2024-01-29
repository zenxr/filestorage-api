import config
import fastapi
from fastapi import staticfiles
from user import routes as user_routes
from filestore import routes as filestore_routes
from auth import routes as auth_routes
from ui import routes as ui

import config

app = fastapi.FastAPI()

app.mount("/static", staticfiles.StaticFiles(directory="ui/static"), name="static")
app.include_router(user_routes.router)
app.include_router(filestore_routes.router)
app.include_router(filestore_routes.bucket_router)
app.include_router(auth_routes.router)
app.include_router(ui.router)

conf = config


@app.get("/")
async def root():
    return fastapi.responses.JSONResponse({"app_name": conf.app_name})


@app.get("/ping")
async def info():
    return fastapi.responses.Response("pong")
