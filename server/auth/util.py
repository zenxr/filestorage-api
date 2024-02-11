import functools
import uuid
import datetime
import logging
import dataclasses

import fastapi

from user import models as usermodels
from . import models as authmodels
import db

sessioncursor = db.ManagedCursor(authmodels.Session)
usercursor = db.ManagedCursor(usermodels.User)

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class InvalidSessionError:
    msg: str


def session_inactivity_duration():
    return datetime.datetime.now() + datetime.timedelta(minutes=30)


def create_session(user: usermodels.User):
    session_id = uuid.uuid4()
    return sessioncursor.fetchone(
        """
        insert into session (id, user_id, valid_to)
        values (%s, %s, %s)
        returning * ;
        """,
        (session_id, user.id, session_inactivity_duration()),
    )


def current_user(request: fastapi.Request):
    if sess_id := request.cookies.get("session_id"):
        return usercursor.fetchone(
            """
            select usr.*
            from session
                join filestorage_user usr on usr.id = session.user_id
            where session.id = %s
            limit 1;
            """,
            (sess_id,),
        )


def refresh_session(request: fastapi.Request):
    def _refresh_session(session_id):
        return sessioncursor.fetchone(
            """
            update session
            set valid_to=%s
            where id=%s and valid_to >= now()
            returning *
            """,
            (session_inactivity_duration(), session_id),
        )

    if not (sess_cookie := request.cookies.get("session_id")):
        return InvalidSessionError(msg="No session ID")

    if not (session := _refresh_session(sess_cookie)):
        return InvalidSessionError(msg="Invalid or expired session ID")
    return session


def authorization_required(func):
    @functools.wraps(func)
    def wrapper(request: fastapi.Request, *args, **kwargs):
        result = refresh_session(request)
        if isinstance(result, InvalidSessionError):
            raise fastapi.HTTPException(
                fastapi.status.HTTP_401_UNAUTHORIZED, detail=result.msg
            )
        return func(request, *args, **kwargs)

    return wrapper
