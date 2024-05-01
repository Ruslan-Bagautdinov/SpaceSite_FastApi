from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from database.postgre_db import get_session
from auth.schemas import UserCreate, User
from database.crud import create_user, get_user_by_username, authenticate_user
from auth.utils import create_access_token

router = APIRouter()


@router.post("/register", response_model=User)
async def register_user(user: UserCreate,
                        db: AsyncSession = Depends(get_session)
                        ):
    db_user = await get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400,
                            detail="Username already registered")
    return await create_user(db=db, user=user)


@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: AsyncSession = Depends(get_session)
                                 ):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
