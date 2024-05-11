from fastapi import (APIRouter,
                     Form,
                     Depends,
                     HTTPException,
                     Request)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgre_db import get_session
from app.auth.schemas import UserCreate, TokenData, User
from app.auth.utils import authenticated_root_redirect
from app.routers.login import check_user
from app.database.crud import (create_user,
                               get_user_by_username)
from templates.icons.icons import USER_REGISTER_ICON


router = APIRouter(tags=['user register'])
templates = Jinja2Templates(directory="templates")


@router.get('/register', response_class=HTMLResponse)
async def register_user(request: Request,
                        user: TokenData | None = Depends(check_user)
                        ):
    return templates.TemplateResponse("user/register.html",
                                      {"request": request,
                                       "user": user},)


@router.post("/register", response_model=User)
async def register_user(request: Request,
                        username: Annotated[str, Form()],
                        email: Annotated[str, Form()],
                        password: Annotated[str, Form()],
                        db: AsyncSession = Depends(get_session)
                        ):
    db_user = await get_user_by_username(db, username=username)
    if db_user:
        raise HTTPException(status_code=400,
                            detail="Username already registered")
    user = UserCreate(username=username, email=email, password=password)
    await create_user(db=db, user=user)
    new_top_message = {
        "class": "alert alert-info rounded",
        "icon": USER_REGISTER_ICON,
        "text": f" account created successfully!"
    }
    request.session['top_message'] = new_top_message
    return await authenticated_root_redirect(user.username)
