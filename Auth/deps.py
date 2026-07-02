from fastapi import Depends, Request, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from Core.Database import get_db
from Auth.JWT_Auth import decode_token, ACCESS_TOKEN_COOKIE_NAME, CSRF_TOKEN_COOKIE_NAME
from Users.Models import UserModel
from Users.SessionModels import RefreshTokenModel

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    bearer: str | None = Depends(bearer_scheme),
) -> UserModel:
    token = request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)

    if not token and bearer:
        token = bearer.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = int(payload["sub"])
    user = db.query(UserModel).filter_by(id=user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


def verify_csrf_token(request: Request):
    cookie_csrf = request.cookies.get(CSRF_TOKEN_COOKIE_NAME)
    header_csrf = request.headers.get("X-CSRF-Token")

    if not cookie_csrf or not header_csrf:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing",
        )

    if cookie_csrf != header_csrf:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token mismatch",
        )
