from fastapi import (APIRouter,
                     Depends,
                     HTTPException,
                     status,
                     Request,
                     Response,
                     Cookie)
from fastapi.security import OAuth2PasswordRequestForm

from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgre_db import get_session
from app.auth.schemas import UserBase, UserCreate, User, TokenData
from app.database.crud import create_user, get_user_by_username, authenticate_user
from app.auth.utils import create_access_token, decode_token
from app.routers.users import get_current_user, credentials_exception
from jwt import PyJWTError
import base64

router = APIRouter(tags=['Protected'])


@router.post('/secret_place')
async def secret_place(request: Request,
                       db: AsyncSession = Depends(get_session)):

    user = await get_current_user(request, db)
    if user:
        return {"message": f"Hello {user['username']}"}
    else:
        raise credentials_exception

