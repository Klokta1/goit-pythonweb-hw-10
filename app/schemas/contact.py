from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date, datetime


class ContactBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50, description="Ім'я контакту")
    last_name: str = Field(..., min_length=1, max_length=50, description="Прізвище контакту")
    email: EmailStr = Field(..., description="Електронна адреса контакту")
    phone_number: str = Field(..., min_length=5, max_length=20, description="Номер телефону контакту")
    birthday: date = Field(..., description="Дата народження контакту")
    additional_data: Optional[str] = Field(None, description="Додаткова інформація про контакт")

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if not all(c.isdigit() or c in ['+', '-', '(', ')', ' '] for c in v):
            raise ValueError("Номер телефону має містити лише цифри та спеціальні символи: +, -, (, ), пробіл")
        return v

    @validator('birthday')
    def validate_birthday(cls, v):
        if v > date.today():
            raise ValueError("Дата народження не може бути в майбутньому")
        return v


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Ім'я контакту")
    last_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Прізвище контакту")
    email: Optional[EmailStr] = Field(None, description="Електронна адреса контакту")
    phone_number: Optional[str] = Field(None, min_length=5, max_length=20, description="Номер телефону контакту")
    birthday: Optional[date] = Field(None, description="Дата народження контакту")
    additional_data: Optional[str] = Field(None, description="Додаткова інформація про контакт")

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is None:
            return v
        if not all(c.isdigit() or c in ['+', '-', '(', ')', ' '] for c in v):
            raise ValueError("Номер телефону має містити лише цифри та спеціальні символи: +, -, (, ), пробіл")
        return v

    @validator('birthday')
    def validate_birthday(cls, v):
        if v is None:
            return v
        if v > date.today():
            raise ValueError("Дата народження не може бути в майбутньому")
        return v


class ContactInDB(ContactBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ContactResponse(ContactInDB):
    pass
