from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.responses import AUTH_ERRORS, ERROR_400, ERROR_422
from app.core.database import get_db
from app.core.exceptions import AuthError, EmailAlreadyRegisteredError
from app.schemas.auth import LoginRequest, RegisterRequest, RegisterResponse, TokenResponse
from app.schemas.user import UserPublic
from app.services import auth_service

router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account. Password is bcrypt-hashed before storage.",
    responses={**ERROR_400, **ERROR_422},
)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if auth_service.get_user_by_email(db, body.email):
        raise EmailAlreadyRegisteredError()
    user = auth_service.create_user(db, body.email, body.password)
    return RegisterResponse(user=UserPublic.model_validate(user))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and obtain a JWT",
    description="Verify credentials and return a bearer token to use as `Authorization: Bearer <token>`.",
    responses=AUTH_ERRORS,
)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, body.email, body.password)
    if not user:
        raise AuthError("Invalid email or password")
    token = auth_service.issue_token_for_user(user)
    return TokenResponse(access_token=token)
