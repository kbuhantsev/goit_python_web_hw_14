from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class ContactSchema(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    surname: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(default=None)
    phone: Optional[str] = Field(default=None)
    date_of_birth: Optional[date] = Field(default=None)

    class ConfigDict:
        from_attributes = True


class ContactSchemaResponse(ContactSchema):
    class ConfigDict:
        from_attributes = True


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=3)

    class ConfigDict:
        from_attributes = True


class UserSchema(UserLoginSchema):
    name: str = Field(min_length=3, max_length=50)
    avatar: Optional[str] = Field(default=None)

    class ConfigDict:
        from_attributes = True


# class UserResponseSchema(BaseModel):
#     user: UserSchema
#     detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
