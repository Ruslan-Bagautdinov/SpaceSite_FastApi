from fastapi import (APIRouter,
                     Depends,
                     HTTPException,
                     status,
                     Request,
                     Response)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


from sqlalchemy.ext.asyncio import AsyncSession
from jwt import PyJWTError

from app.database.postgre_db import get_session
from app.auth.schemas import TokenData
from app.database.crud import (get_user,
                               get_user_by_username,
                               authenticate_user)
from app.auth.utils import decode_token, create_access_token
from app.routers.login import get_current_user


router = APIRouter(tags=['user profile'])

templates = Jinja2Templates(directory="templates")


@router.get("/me")
async def get_me(request: Request,
                 db: AsyncSession = Depends(get_session)):
    user = await get_current_user(request, db)
    if user:
        return {"message": f"Hello {user['username']}, your ID is {user['id']}"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please log in to access this page",
            headers={"WWW-Authenticate": "Bearer"},
        )
