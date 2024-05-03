from fastapi import (APIRouter,
                     Depends,
                     HTTPException,
                     status,
                     Request)
from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgre_db import get_session
from app.auth.schemas import UserCreate, User
from app.database.crud import (create_user,
                               get_user_by_username)


router = APIRouter(tags=['user register'])
templates = Jinja2Templates(directory="templates")


@router.get('/register')
async def register_user(request: Request):
    data = 'Welcome to our website!'
    return templates.TemplateResponse("base.html",
                                      {"request": request,
                                       "data": data
                                       }
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
