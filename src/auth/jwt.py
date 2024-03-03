from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import secrets

# Токены валидны пока программа работает и не истекло время жизни токена
jwt_session_secret = secrets.token_urlsafe(32)


def mintJWT(subject: str, extras: dict) -> str:
    return jwt.encode(
        {
            "sub": subject,
            "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=15),
            **extras,
        },
        jwt_session_secret,
        algorithm="HS256",
    )


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if not credentials:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")
        if not credentials.scheme == "Bearer":
            raise HTTPException(
                status_code=403, detail="Invalid authentication scheme."
            )
        try:
            payload = jwt.decode(
                credentials.credentials, jwt_session_secret, algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=403, detail="Token has expired.")
        except jwt.PyJWTError:
            raise HTTPException(status_code=403, detail="Token is invalid.")
        raise HTTPException(status_code=403, detail="Could not validate credentials.")
