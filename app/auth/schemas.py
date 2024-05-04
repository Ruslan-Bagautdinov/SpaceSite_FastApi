from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    username: str
    email: str
    password: str

    class Config:
        from_attributes = True


class UserProfileUpdate(User):
    first_name: str
    last_name: str
    phone_number: str
    photo: str


class TokenData(BaseModel):
    username: str | None = None
