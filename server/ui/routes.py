import fastapi
from fastapi import templating
from auth import util as authutils

router = fastapi.APIRouter(
    prefix="/ui",
    tags=["frontend", "ui", "templates"],
    responses={404: {"description": "Not found"}},
)

templates = templating.Jinja2Templates(directory="./ui/templates")


@router.get("/", response_class=fastapi.responses.HTMLResponse)
async def index(request: fastapi.Request):
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
