from fastapi import Response

from Auth.JWT_Auth import (
    ACCESS_TOKEN_COOKIE_NAME,
    REFRESH_TOKEN_COOKIE_NAME,
    CSRF_TOKEN_COOKIE_NAME,
    ACCESS_COOKIE_MAX_AGE,
    REFRESH_COOKIE_MAX_AGE,
)


def set_access_cookie(response: Response, token: str):
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=token,
        max_age=ACCESS_COOKIE_MAX_AGE,
        httponly=True,
        secure=True,
        samesite="strict",
    )


def set_refresh_cookie(response: Response, token: str):
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=token,
        max_age=REFRESH_COOKIE_MAX_AGE,
        httponly=True,
        secure=True,
        samesite="strict",
    )


def set_csrf_cookie(response: Response, token: str):
    response.set_cookie(
        key=CSRF_TOKEN_COOKIE_NAME,
        value=token,
        max_age=REFRESH_COOKIE_MAX_AGE,
        httponly=False,
        secure=True,
        samesite="strict",
    )


def clear_auth_cookies(response: Response):
    response.delete_cookie(key=ACCESS_TOKEN_COOKIE_NAME)
    response.delete_cookie(key=REFRESH_TOKEN_COOKIE_NAME)
    response.delete_cookie(key=CSRF_TOKEN_COOKIE_NAME)
