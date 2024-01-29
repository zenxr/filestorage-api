import logging

import fastapi
from fastapi import security

from . import models as authmodels
from . import util as authutil
from user import models as usermodels
from user import schemas as userschemas
import db

logger = logging.getLogger(__name__)

usercursor = db.ManagedCursor(usermodels.User)
sessioncursor = db.ManagedCursor(authmodels.Session)

_security = security.HTTPBasic()

router = fastapi.routing.APIRouter(
    prefix="/auth",
    tags=["users", "auth"],
    responses={404: {"description": "Not found"}},
)


@router.post("/login")
def login(credentials: security.HTTPBasicCredentials = fastapi.Depends(_security)):
    user = usercursor.fetchone(
        "select * from filestorage_user where username=%s", (credentials.username,)
    )
    if not (user and user.check_password(credentials.password)):
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW_Authenticate": "Basic"},
        )
    session = authutil.create_session(user)
    if not session:
        # TODO: handle via generalized error handlers
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
            headers={"WWW_Authenticate": "Basic"},
        )
    response = fastapi.responses.JSONResponse(
        {"message": "Logged in successfully", "session_id": str(session.id)}
    )
    response.headers.update({"HX-Redirect": "/ui"})
    # TODO: `expires` requires UTC offset, some incantation like...
    # response.set_cookie(key="session_id", value=str(session.id), expires=session.valid_to)
    response.set_cookie(key="session_id", value=str(session.id))
    return response


@authutil.authorization_required
@router.get("/me", response_model=userschemas.OutUser)
def current_user(request: fastapi.Request):
    if session_id := request.cookies.get("session_id"):
        query = """
        select filestorage_user.*
        from filestorage_user
        , session
        where session.id=%s
            and filestorage_user.id = session.user_id
        """
        if user := usercursor.fetchone(query, (session_id,)):
            return user
    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED, detail="Invalid session ID"
    )


@router.post("/logout")
def logout(request: fastapi.Request):
    if session_id := request.cookies.get("session_id"):
        if not sessioncursor.fetchone(
            "delete from session where id=%s returning *;", (session_id,)
        ):
            return fastapi.HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session ID",
            )
        response = fastapi.responses.JSONResponse(
            {"message": "Logged out successfully"}
        )
        response.headers.update({"HX-Redirect": "/ui"})
        response.delete_cookie(key="session_id")
        return response
