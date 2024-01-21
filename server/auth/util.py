import functools
import uuid
import datetime
import logging

import fastapi

from user import models as usermodels
from . import models as authmodels
import db

sessioncursor = db.ManagedCursor(authmodels.Session)
usercursor = db.ManagedCursor(usermodels.User)

logger = logging.getLogger(__name__)


def session_inactivity_duration():
    return datetime.datetime.now() + datetime.timedelta(minutes=30)


def refresh_session(session_id):
    return sessioncursor.fetchone(
        """
        update session
        set valid_to=%s
        where id=%s and valid_to >= now()
        returning *
        """,
        (session_inactivity_duration(), session_id),
    )


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


def authorization_required(func):
    @functools.wraps(func)
    def wrapper(request: fastapi.Request, *args, **kwargs):
        if not (sess_cookie := request.cookies.get("session_id")):
            return fastapi.HTTPException(
                fastapi.status.HTTP_401_UNAUTHORIZED, detail="Invalid session ID"
            )

        if not (session := refresh_session(sess_cookie)):
            return fastapi.HTTPException(
                fastapi.status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session ID",
            )
        return func(request, *args, **kwargs)

    return wrapper
