from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


# Ro'yxatdan o'tish so'rovi uchun
class UserCreate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50, description="Foydalanuvchining ismi")
    last_name: str = Field(..., min_length=2, max_length=50, description="Foydalanuvchining familiyasi")
    email: EmailStr = Field(..., description="Foydalanuvchining email manzili")
    phone_number: str = Field(..., description="Telefon raqami (masalan: +998901234567)")
    password: str = Field(..., min_length=6, description="Parol (kamida 6 ta belgi)")

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Probeller hamda keraksiz belgilardan tozalash
        cleaned = re.sub(r"[\s\-\(\)]", "", v)
        if not re.match(r"^\+?[0-9]{9,15}$", cleaned):
            raise ValueError("Telefon raqami noto'g me'yorda (masalan: +998901234567)")
        return cleaned


# Login so'rovi uchun
class UserLogin(BaseModel):
    phone_number: str = Field(..., description="Telefon raqami")
    password: str = Field(..., description="Parol")

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"[\s\-\(\)]", "", v)
        if not cleaned:
            raise ValueError("Telefon raqami kiritilishi shart")
        return cleaned


# Token javobi uchun
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# User ma'lumotlarini qaytarish uchun
class UserOut(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    is_active: bool
    is_superuser: bool
    created_at: datetime

    class Config:
        from_attributes = True