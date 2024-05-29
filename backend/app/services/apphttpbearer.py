"""Class AppHttpBearer is a helper to protect routes

    Raises:
        HTTPException: jwt.ExpiredSignatureError, 401 Token expired
        HTTPException: jwt.InvalidTokenError, 401 invalid token

    Returns:
        JSONResponse: status_code 200 and message valid token
"""
from typing import Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException
import jwt
from app.resources.required_packages import ALGORITHM, SECRET_KEY
from app.models.user import User


class AppHttpBearer(HTTPBearer):
    """
    Class AppHttpBearer Inherits from the HTTPBearer class.
    The (check_session) property is set (True) when the oauth
    is for an endpoint that requires the user to be logged in
    and (False) for the others oauth.
    """

    def __init__(self, auto_error: bool = True, check_session: bool = False):
        self.check_session = check_session
        super().__init__(auto_error=auto_error)

    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        res = await super().__call__(request)
        try:
            decoded_token = jwt.decode(
                res.credentials, SECRET_KEY, algorithms=[ALGORITHM]
            )
            if self.check_session:
                email = decoded_token["sub"]
                user = User(email=email)
                # If the user isn't connected, his token won't work
                if user.is_session_active() == 0:
                    raise HTTPException(401, "Token expired")
            return decoded_token
        except jwt.ExpiredSignatureError as exc:
            # Token has expired
            raise HTTPException(401, "Token expired") from exc
        except jwt.InvalidTokenError as exc:
            # Invalid token
            raise HTTPException(401, "invalid Token") from exc
