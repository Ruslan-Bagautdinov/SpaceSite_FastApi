from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import os

from app.database.models import User, UserProfile
from app.auth.schemas import UserCreate, UserProfileUpdate
from app.auth.utils import get_password_hash, verify_password


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user(db: AsyncSession, user_id: int):
    result = await db.get(User, user_id)
    return result


async def get_user_profile(db: AsyncSession, user_id: int):
    user_profile = await db.get(UserProfile, user_id)
    return user_profile


async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username,
                   hashed_password=hashed_password,
                   email=user.email)
    db.add(db_user)
    await db.flush()
    db_user_profile = UserProfile(user_id=db_user.id)
    db.add(db_user_profile)
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
    result = await db.execute(select(UserProfile).where(UserProfile.id == user_id))
    db_user = result.scalars().first()
    if db_user:
        if user_profile.first_name is not None:
            db_user.first_name = user_profile.first_name
        if user_profile.last_name is not None:
            db_user.last_name = user_profile.last_name
        if user_profile.phone_number is not None:
            db_user.phone_number = user_profile.phone_number
        if user_profile.user_photo is not None:
            db_user.user_photo = user_profile.user_photo
        if user_profile.user_age is not None:
            db_user.user_age = user_profile.user_age
        await db.commit()
        await db.refresh(db_user)
        return db_user
    else:
        raise HTTPException(status_code=404, detail="User not found")


async def delete_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id).options(selectinload(User.profile)))
    db_user = result.scalars().first()

    if db_user:
        await db.delete(db_user)
        await db.commit()
        return True
    return False
