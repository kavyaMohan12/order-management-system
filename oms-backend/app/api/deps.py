from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AuthError
from app.core.security import decode_token
from app.models import User

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthError("Not authenticated")
    user_id_str = decode_token(credentials.credentials)
    if user_id_str is None:
        raise AuthError("Invalid or expired token")
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise AuthError("Invalid or expired token")
    user = db.get(User, user_id)
    if user is None:
        raise AuthError("Invalid or expired token")
    return user
