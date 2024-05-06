from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgre_db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(index=True)

    profile: Mapped["UserProfile"] = relationship(back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)
    first_name: Mapped[str] = mapped_column(index=True, nullable=True)
    last_name: Mapped[str] = mapped_column(index=True, nullable=True)
    phone_number: Mapped[str] = mapped_column(index=True, nullable=True)
    photo: Mapped[str] = mapped_column(index=True, nullable=True)
    ass_size: Mapped[int] = mapped_column(index=True, nullable=True)

    user: Mapped[User] = relationship(back_populates="profile")


