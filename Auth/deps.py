from fastapi import Depends, Request, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from Core.Database import get_db
from Core.i18n import detect_language, get_translations
from Auth.JWT_Auth import decode_token, ACCESS_TOKEN_COOKIE_NAME, CSRF_TOKEN_COOKIE_NAME
from Users.Models import UserModel
bearer_scheme = HTTPBearer(auto_error=False)


def _(request: Request, key: str) -> str:
    lang = detect_language(request)
    t = get_translations(lang)
    return t.gettext(key)


def _extract_token(request: Request, bearer: str | None) -> str:
    token = request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    if not token and bearer:
        token = bearer.credentials
    return token


def _decode_access_token(token: str, request: Request) -> dict:
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_(request, "invalid_token"),
        )
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_(request, "invalid_token_type"),
        )
    return payload


def _get_active_user(db: Session, user_id: int, request: Request) -> UserModel:
    user = db.query(UserModel).filter_by(id=user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_(request, "user_not_found_or_inactive"),
        )
    return user


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    bearer: str | None = Depends(bearer_scheme),
) -> UserModel:
    token = _extract_token(request, bearer)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_(request, "not_authenticated"),
        )

    payload = _decode_access_token(token, request)
    user_id = int(payload["sub"])
    return _get_active_user(db, user_id, request)


def verify_csrf_token(request: Request):
    cookie_csrf = request.cookies.get(CSRF_TOKEN_COOKIE_NAME)
    header_csrf = request.headers.get("X-CSRF-Token")

    if not cookie_csrf or not header_csrf:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_(request, "csrf_token_missing"),
        )

    if cookie_csrf != header_csrf:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_(request, "csrf_token_mismatch"),
        )
