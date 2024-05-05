from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.auth.schemas import UserCreate, UserProfileUpdate
from app.auth.utils import get_password_hash, verify_password


async def get_user(db: AsyncSession, user_id: int):
    result = await db.get(User, user_id)
    return result


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username,
                   hashed_password=hashed_password,
                   email=user.email)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def update_user_profile(db: AsyncSession, user_id: int, user_profile: UserProfileUpdate):
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()
    if db_user:
        if user_profile.first_name is not None:
            db_user.first_name = user_profile.first_name
        if user_profile.last_name is not None:
            db_user.last_name = user_profile.last_name
        if user_profile.phone_number is not None:
            db_user.phone_number = user_profile.phone_number
        if user_profile.photo is not None:
            db_user.photo = user_profile.photo
        if user_profile.ass_size is not None:
            db_user.ass_size = user_profile.ass_size
        await db.commit()
        await db.refresh(db_user)
        return db_user
    else:
        raise HTTPException(status_code=404, detail="User not found")
