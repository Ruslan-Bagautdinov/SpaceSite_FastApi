from sqlalchemy.orm import Mapped, mapped_column

from app.database.postgre_db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(index=True)
    email: Mapped[str] = mapped_column(index=True)
    hashed_password: Mapped[str] = mapped_column(index=True)
    first_name: Mapped[str] = mapped_column(index=True, nullable=True)
    last_name: Mapped[str] = mapped_column(index=True, nullable=True)
    phone_number: Mapped[str] = mapped_column(index=True, nullable=True)
    photo: Mapped[str] = mapped_column(index=True, nullable=True)
    first_name: Mapped[str] = mapped_column(index=True, nullable=True)
    last_name: Mapped[str] = mapped_column(index=True, nullable=True)
    phone_number: Mapped[str] = mapped_column(index=True, nullable=True)
    photo: Mapped[str] = mapped_column(index=True, nullable=True)
    ass_size: Mapped[str] = mapped_column(index=True, nullable=True)
