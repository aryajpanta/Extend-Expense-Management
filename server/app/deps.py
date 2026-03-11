from __future__ import annotations

from datetime import datetime

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .models import Session as UserSession
from .models import User
from .security import unsign_session_token


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    settings = get_settings()
    cookie = request.cookies.get(settings.session_cookie_name)
    if not cookie:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    session_id = unsign_session_token(cookie)
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    session = db.get(UserSession, session_id)
    if session is None or session.expires_at <= datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    return session.user

