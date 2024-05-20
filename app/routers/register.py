from fastapi import (APIRouter,
                     Form,
                     Depends,
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
from app.tools.functions import redirect_with_message
from templates.icons import WARNING_ICON, WARNING_CLASS, USER_REGISTER_ICON


router = APIRouter(tags=['user register'])
templates = Jinja2Templates(directory="templates")


@router.get('/register', response_class=HTMLResponse)
async def register_user(request: Request,
                        user: TokenData | None = Depends(check_user)
                        ):
    top_message = request.session.get('top_message')
    if top_message:
        request.session.pop('top_message', None)

    return templates.TemplateResponse("user/register.html",
                                      {"request": request,
                                       "user": user,
                                       "top_message": top_message
                                       }
                                      )


@router.post("/register", response_model=User)
async def register_user(request: Request,
                        username: Annotated[str, Form()],
                        email: Annotated[str, Form()],
                        password: Annotated[str, Form()],
                        db: AsyncSession = Depends(get_session)
                        ):
    db_user = await get_user_by_username(db, username=username)
    if db_user:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text=f"Username {username} is already registered!",
                                           endpoint="/register"
                                           )
    user = UserCreate(username=username, email=email, password=password)
    await create_user(db=db, user=user)
    new_top_message = {
        "class": "alert alert-info rounded",
        "icon": USER_REGISTER_ICON,
        "text": f"User {username} has been created"
    }
    request.session['top_message'] = new_top_message
    return await authenticated_root_redirect(request, user.username)
