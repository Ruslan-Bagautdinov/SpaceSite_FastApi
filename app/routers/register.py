from typing import Annotated

from fastapi import (APIRouter,
                     Form,
                     Depends,
                     Request)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import UserCreate, TokenData, User
from app.auth.utils import authenticated_root_redirect
from app.database.crud import (create_user,
                               check_user_exists)
from app.database.postgre_db import get_session
from app.routers.login import check_user
from app.tools.functions import redirect_with_message
from templates.icons import WARNING_ICON, WARNING_CLASS, USER_REGISTER_ICON

router = APIRouter(tags=['user register'])
templates = Jinja2Templates(directory="templates")


@router.get('/register', response_class=HTMLResponse, description="Display the registration form.")
async def register_user(request: Request,
                        user: TokenData | None = Depends(check_user)
                        ):
    """
    Display the registration form.

    Args:
        request (Request): The request object.
        user (TokenData): The authenticated user data.

    Returns:
        TemplateResponse: The rendered HTML template for the registration form.
    """
    top_message = request.session.get('top_message')
    if top_message:
        request.session.pop('top_message', None)

    return templates.TemplateResponse("user/register.html",
                                      {"request": request,
                                       "user": user,
                                       "top_message": top_message
                                       }
                                      )


@router.post("/register", response_model=User, description="Register a new user.")
async def register_user(request: Request,
                        username: Annotated[str, Form()],
                        email: Annotated[str, Form()],
                        password: Annotated[str, Form()],
                        db: AsyncSession = Depends(get_session)
                        ):
    """
    Register a new user.

    Args:
        request (Request): The request object.
        username (str): The username of the new user.
        email (str): The email of the new user.
        password (str): The password of the new user.
        db (AsyncSession): The database session.

    Returns:
        RedirectResponse: Redirect to the root page after successful registration.
    """
    existing_user_check = await check_user_exists(db, username=username, email=email)
    if existing_user_check == "username":
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text=f"Username {username} is already registered!",
                                           endpoint="/register"
                                           )
    elif existing_user_check == "email":
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text=f"Email {email} is already registered!",
                                           endpoint="/register"
                                           )
    elif existing_user_check == "both":
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text=f"Username {username} and Email {email} are already registered!",
                                           endpoint="/register"
                                           )

    user = UserCreate(username=username, email=email, password=password, role="user")
    await create_user(db=db, user=user)
    new_top_message = {
        "class": "alert alert-info rounded",
        "icon": USER_REGISTER_ICON,
        "text": f"User {username} has been created"
    }
    request.session['top_message'] = new_top_message
    return await authenticated_root_redirect(request, user.username, role="user")
