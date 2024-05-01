from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    email: str


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    username: str | None = None
