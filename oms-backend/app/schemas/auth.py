from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.user import UserPublic


class RegisterRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "user@example.com", "password": "supersecret1"}
        }
    )

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "user@example.com", "password": "supersecret1"}
        }
    )

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    user: UserPublic
