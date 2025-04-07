from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    designer = "designer"


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(None, min_length=2, max_length=50)
    role: Optional[UserRole] = UserRole.user


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=50)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserInDB(UserBase):
    id: int
    disabled: bool = False
    google_id: Optional[str] = None
    hashed_password: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
