from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Ім'я користувача")
    email: EmailStr = Field(..., description="Електронна адреса користувача")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Пароль користувача")

    @validator('password')
    def validate_password(cls, v):
        if not any(char.isupper() for char in v):
            raise ValueError("Пароль повинен містити хоча б одну велику літеру")
        if not any(char.islower() for char in v):
            raise ValueError("Пароль повинен містити хоча б одну малу літеру")
        if not any(char.isdigit() for char in v):
            raise ValueError("Пароль повинен містити хоча б одну цифру")
        if not any(char in "!@#$%^&*()_-+=<>?/" for char in v):
            raise ValueError("Пароль повинен містити хоча б один спеціальний символ")
        return v


class UserInDB(UserBase):
    id: int
    avatar: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    confirmed: bool = False

    class Config:
        orm_mode = True


class UserResponse(UserBase):
    id: int
    avatar: Optional[str] = None
    created_at: datetime
    confirmed: bool

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Ім'я користувача")

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


class EmailSchema(BaseModel):
    email: EmailStr
