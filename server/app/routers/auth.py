from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..deps import get_current_user
from ..models import Session as UserSession
from ..models import User
from ..schemas import LoginRequest, SessionResponse
from ..security import generate_session_token, session_expiry, sign_session_token, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=SessionResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> SessionResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    settings = get_settings()
    token = generate_session_token()
    session = UserSession(id=token, user_id=user.id, expires_at=session_expiry(settings.session_days))
    db.add(session)
    db.commit()

    response.set_cookie(
        key=settings.session_cookie_name,
        value=sign_session_token(token),
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.session_days * 24 * 60 * 60,
    )
    return SessionResponse(authenticated=True, userEmail=user.email)


@router.post("/logout", response_model=SessionResponse)
def logout(response: Response, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> SessionResponse:
    settings = get_settings()
    for session in list(user.sessions):
        db.delete(session)
    db.commit()
    response.delete_cookie(settings.session_cookie_name)
    return SessionResponse(authenticated=False, userEmail=None)


@router.get("/session", response_model=SessionResponse)
def session(user: User = Depends(get_current_user)) -> SessionResponse:
    return SessionResponse(authenticated=True, userEmail=user.email)

