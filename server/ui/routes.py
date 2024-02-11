import dataclasses
import logging

import fastapi
from fastapi import templating

from auth import util as authutils
from user import service as userservice

logger = logging.getLogger(__name__)

router = fastapi.APIRouter(
    prefix="/ui",
    tags=["frontend", "ui", "templates"],
    responses={404: {"description": "Not found"}},
)

templates = templating.Jinja2Templates(directory="./ui/templates")

@router.get("/", response_class=fastapi.responses.HTMLResponse)
async def index(request: fastapi.Request):
    if not (authutils.current_user(request)):
        response = fastapi.responses.RedirectResponse(
            url="/ui/login"
        )
        response.delete_cookie(key="session_id")
        return response

    return templates.TemplateResponse(
        request=request, name="index.html.jinja2", context={}
    )


@router.get("/navbar", response_class=fastapi.responses.HTMLResponse)
async def navbar(request: fastapi.Request):
    user_logged_in = bool(authutils.current_user(request))
    return templates.TemplateResponse(
        request=request,
        name="navbar.html.jinja2",
        context={"logged_in": user_logged_in},
    )


@router.get("/login", response_class=fastapi.responses.HTMLResponse)
async def login(request: fastapi.Request):
    return templates.TemplateResponse(
        request=request, name="login.html.jinja2", context={}
    )


@router.get("/signup", response_class=fastapi.responses.HTMLResponse)
async def signup(request: fastapi.Request):
    return templates.TemplateResponse(
        request=request, name="signup.html.jinja2", context={}
    )

@authutils.authorization_required
@router.get("/users", response_class=fastapi.responses.HTMLResponse)
async def users_table(request: fastapi.Request):
    users = userservice.fetch_users()
    users.sort(key=lambda u: u.id)
    # notice users have salted passwords, but the template doesn't access the
    # attribute -- we don't have to worry about exposing because template is
    # generated server side
    return templates.TemplateResponse(
        request=request, name="users.html.jinja2", context={
            'users': [dataclasses.asdict(u) for u in users]
        }
    )
