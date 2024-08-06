from datetime import datetime

from sqlalchemy import ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgre_db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(index=True)

    profile: Mapped["UserProfile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    posts: Mapped[list["Post"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    first_name: Mapped[str] = mapped_column(index=True, nullable=True)
    last_name: Mapped[str] = mapped_column(index=True, nullable=True)
    phone_number: Mapped[str] = mapped_column(index=True, nullable=True)
    user_photo: Mapped[str] = mapped_column(index=True, nullable=True)
    user_age: Mapped[int] = mapped_column(index=True, nullable=True)

    user: Mapped[User] = relationship(back_populates="profile")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    content: Mapped[str] = mapped_column(Text, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="posts")

    def truncated_content(self):
        return self.content[:300] + '...' if len(self.content) > 300 else self.content
