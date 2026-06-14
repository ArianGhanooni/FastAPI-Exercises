from datetime import timedelta
from datetime import datetime
from datetime import timezone

from uuid import uuid4

import jwt

SECRET_KEY = "CHANGE_ME_IN_PRODUCTION"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

ACCESS_TOKEN_COOKIE_NAME = "access_token"
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"

ACCESS_COOKIE_MAX_AGE = int(timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds())

REFRESH_COOKIE_MAX_AGE = int(timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())


def create_access_token(user_id: int):

    expire = (datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: int):

    jti = str(uuid4())

    expire = (datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": jti,
        "exp": expire
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token, jti, expire


def decode_token(token: str):

    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])