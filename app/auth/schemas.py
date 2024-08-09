from typing import Optional

from pydantic import BaseModel, field_validator


class UserBase(BaseModel):
    username: str
    email: str
    role: str

    @field_validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'admin']:
            raise ValueError('Role must be either "user" or "admin"')
        return v


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    user_photo: Optional[str] = None
    user_age: Optional[int] = None
    role: Optional[str] = None  # Add role field

    @field_validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'admin']:
            raise ValueError('Role must be either "user" or "admin"')
        return v

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None
