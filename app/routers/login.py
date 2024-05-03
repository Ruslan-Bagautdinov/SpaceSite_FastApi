from fastapi import (APIRouter,
                     Depends,
                     HTTPException,
                     status,
                     Request,
                     Response)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates


from sqlalchemy.ext.asyncio import AsyncSession
from jwt import PyJWTError

from app.database.postgre_db import get_session
from app.auth.schemas import TokenData
from app.database.crud import (get_user,
                               get_user_by_username,
                               authenticate_user)
from app.auth.utils import credentials_exception, decode_token, create_access_token


router = APIRouter(tags=['user login'])

templates = Jinja2Templates(directory="templates")


async def get_current_user(request: Request,
                           db: AsyncSession = Depends(get_session)):

    access_token = request.cookies.get("access_token")

    if access_token is None:
        raise credentials_exception
    try:
        payload = decode_token(access_token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception

    user = await get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception

    user_data = await get_user(db, user.id)
    return user_data


async def check_if_logged(request: Request):
    access_token = request.cookies.get("access_token")

    if access_token is None:
        return None
    try:
        payload = decode_token(access_token)
        username: str = payload.get("sub")
        if username is None:
            return None
        else:
            return username
    except PyJWTError:
        return None


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
    response = JSONResponse(content={"token_type": "bearer"})
    response.set_cookie(
        "access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=False,
        samesite='lax',
        max_age=1800,
        expires=1800,
    )
    return response


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logout successful"}


@router.post("/me")
async def get_me(request: Request,
                 db: AsyncSession = Depends(get_session)):
    user = get_current_user(request, db)
    return user


