from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session

from Core.Database import get_db
from Core.Security import hash_password, verify_password
from Core.i18n import detect_language, get_translations
from Users.Models import UserModel
from Users.SessionModels import RefreshTokenModel
from Auth.Schema import LoginSchema, RegisterSchema, UserResponse, RefreshResponse
from Auth.JWT_Auth import (
    create_access_token,
    create_refresh_token,
    create_csrf_token,
    decode_token,
    REFRESH_TOKEN_COOKIE_NAME,
)
from Auth.utils import (
    set_access_cookie,
    set_refresh_cookie,
    set_csrf_cookie,
    clear_auth_cookies,
)
from Auth.deps import get_current_user, verify_csrf_token

router = APIRouter(prefix="/auth", tags=["auth"])


def _(request: Request, key: str) -> str:
    lang = detect_language(request)
    t = get_translations(lang)
    return t.gettext(key)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: Request, data: RegisterSchema, db: Session = Depends(get_db)):
    if db.query(UserModel).filter_by(username=data.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_(request, "register_username_taken"),
        )

    if db.query(UserModel).filter_by(email=data.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_(request, "register_email_taken"),
        )

    user = UserModel(
        username=data.username,
        email=data.email,
        password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", status_code=status.HTTP_200_OK)
def login(request: Request, data: LoginSchema, response: Response, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter_by(username=data.username).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_(request, "login_invalid_credentials"),
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_(request, "login_account_disabled"),
        )

    access_token = create_access_token(user.id)
    refresh_token, jti, expires_at = create_refresh_token(user.id)
    csrf_token = create_csrf_token()

    session = RefreshTokenModel(
        user_id=user.id,
        token_jti=jti,
        expires_at=expires_at,
    )
    db.add(session)
    db.commit()

    set_access_cookie(response, access_token)
    set_refresh_cookie(response, refresh_token)
    set_csrf_cookie(response, csrf_token)

    return {
        "message": _(request, "login_success"),
        "csrf_token": csrf_token,
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    _csrf: None = Depends(verify_csrf_token),
):
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)

    if refresh_token:
        try:
            payload = decode_token(refresh_token)
            jti = payload.get("jti")
            if jti:
                db.query(RefreshTokenModel).filter_by(token_jti=jti).delete()
                db.commit()
        except Exception:
            pass

    clear_auth_cookies(response)
    return {"message": _(request, "logout_success")}


@router.post("/refresh", status_code=status.HTTP_200_OK)
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_(request, "refresh_token_not_found"),
        )

    try:
        payload = decode_token(refresh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_(request, "refresh_token_invalid"),
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_(request, "refresh_token_invalid_type"),
        )

    jti = payload.get("jti")
    session = db.query(RefreshTokenModel).filter_by(token_jti=jti).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_(request, "refresh_token_revoked"),
        )

    db.delete(session)
    db.commit()

    user_id = int(payload["sub"])
    user = db.query(UserModel).filter_by(id=user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_(request, "refresh_token_user_not_found"),
        )

    new_access_token = create_access_token(user.id)
    new_refresh_token, new_jti, new_expires_at = create_refresh_token(user.id)
    csrf_token = create_csrf_token()

    new_session = RefreshTokenModel(
        user_id=user.id,
        token_jti=new_jti,
        expires_at=new_expires_at,
    )
    db.add(new_session)
    db.commit()

    set_access_cookie(response, new_access_token)
    set_refresh_cookie(response, new_refresh_token)
    set_csrf_cookie(response, csrf_token)

    return {
        "message": _(request, "token_refreshed"),
        "csrf_token": csrf_token,
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserModel = Depends(get_current_user)):
    return current_user
