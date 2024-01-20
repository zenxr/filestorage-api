import config
import fastapi
from user import routes as user_routes
from filestore import routes as filestore_routes
from auth import routes as auth_routes

import config

app = fastapi.FastAPI()

app.include_router(user_routes.router)
app.include_router(filestore_routes.router)
app.include_router(auth_routes.router)

conf = config

@app.get("/")
async def root():
    return fastapi.responses.JSONResponse({"app_name": conf.app_name})


@app.get("/ping")
async def info():
    return fastapi.responses.Response("pong")

