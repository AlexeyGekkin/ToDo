from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    field_validator,
)


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    timezone: str

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError("Invalid timezone")

        return value


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    timezone: str

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"