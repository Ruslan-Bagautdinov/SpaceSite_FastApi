from fastapi import (APIRouter,
                     Depends,
                     HTTPException,
                     status,
                     Request)
from fastapi.security import OAuth2PasswordRequestForm

from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgre_db import get_session
from app.auth.schemas import UserCreate, User, TokenData
from app.database.crud import (create_user,
                               get_user,
                               get_user_by_username,
                               authenticate_user)
from app.auth.utils import create_access_token, decode_token

from jwt import PyJWTError
import base64

router = APIRouter(tags=['users'])

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


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
    encoded_token = base64.b64encode(access_token).decode('utf-8')

    response = JSONResponse(content={"token_type": "bearer"})

    response.set_cookie(
        "access_token",
        value=f"Bearer {encoded_token}",
        httponly=True,
        secure=False,
        samesite='lax',
        max_age=1800,
        expires=1800,
    )

    return response


@router.post("/logout")
async def logout_user():
    ...


@router.post("/me")
async def get_current_user(request: Request,
                           db: AsyncSession = Depends(get_session)):

    access_token = request.cookies.get("access_token")

    if access_token is None:
        raise credentials_exception
    access_token = access_token.replace("Bearer ", "")

    decoded_token = base64.b64decode(access_token).decode('utf-8')

    try:
        payload = decode_token(decoded_token)

        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError as e:
        print(e)
        raise credentials_exception

    user = await get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception

    user_data = await get_user(db, user.id)
    return user_data
