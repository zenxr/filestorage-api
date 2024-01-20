import uuid
import datetime

import fastapi
from fastapi import security

from . import models as authmodels
from user import models as usermodels
from user import schemas as userschemas
import db

usercursor = db.ManagedCursor(usermodels.User)
sessioncursor = db.ManagedCursor(authmodels.Session)

_security = security.HTTPBasic()

router = fastapi.routing.APIRouter(
    prefix="/auth/",
    tags=["users", "auth"],
    responses={404: {"description": "Not found"}},
)


# TODO: session auth
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
    session = create_session(user)
    if not session:
        # TODO: handle via generalized error handlers
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
            headers={"WWW_Authenticate": "Basic"},
        )
    response = fastapi.responses.JSONResponse(
        {"message": "Logged in successfully", "session_id": session.id}
    )
    response.set_cookie("session_id", session.id)


def create_session(user: usermodels.User):
    session_id = uuid.uuid4()
    valid_to = datetime.datetime.now() + datetime.timedelta(days=2)
    return sessioncursor.fetchone(
        "insert into session (id, user_id, valid_to)", (session_id, user.id, valid_to)
    )

@router.get("/me", response_model=userschemas.OutUser)
def current_user(request: fastapi.Request):
    if session_id := request.cookies.get("session_id"):
        query = "".join(
            [
                "select filestorage_user.*",
                "from session"
                "join filestorage_user on session.user_id = filestorage_user.id",
                "where session.id = %s",
            ]
        )
        if user := usercursor.fetchone(query, session_id):
            return user
    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED, detail="Invalid session ID"
    )


@router.post("/logout")
def logout(request: fastapi.Request):
    if session_id := request.cookies.get("session_id"):
        session = sessioncursor.fetchone(
            "delete from sessions where id=%s", (session_id,)
        )
        if session:
            return {"message": "Logged out successfully", "session_id": session.id}
    return fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED, detail="Invalid session ID"
    )

# TODO: session middleware
# should be registerable @ router or route level. Intentionally don't want @ app
# level.
