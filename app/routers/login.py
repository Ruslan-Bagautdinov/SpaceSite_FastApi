# login.py
from fastapi import (APIRouter,
                     Depends,
                     status,
                     Request)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import check_user
from app.auth.schemas import TokenData
from app.auth.utils import (authenticated_root_redirect,
                            clear_tokens_in_cookies)
from app.database.crud import (authenticate_user)
from app.database.postgre_db import get_session
from app.tools.functions import redirect_with_message
from templates.icons import WARNING_ICON, WARNING_CLASS

router = APIRouter(tags=['user login'])

templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse, description="Display the login form.")
async def get_login(request: Request,
                    user: TokenData | None = Depends(check_user)):
    """
    Display the login form.

    Args:
        request (Request): The request object.
        user (TokenData): The authenticated user data.

    Returns:
        TemplateResponse: The rendered HTML template for the login form.
    """
    top_message = request.session.get('top_message')
    if top_message:
        request.session.pop('top_message', None)

    return templates.TemplateResponse("user/login.html",
                                      {"request": request,
                                       "user": user,
                                       "top_message": top_message
                                       }
                                      )


@router.post("/login", description="Authenticate user and redirect to the root page.")
async def login_for_access_token(request: Request,
                                 form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: AsyncSession = Depends(get_session)
                                 ):
    """
    Authenticate user and redirect to the root page.

    Args:
        request (Request): The request object.
        form_data (OAuth2PasswordRequestForm): The form data containing username and password.
        db (AsyncSession): The database session.

    Returns:
        RedirectResponse: Redirect to the root page after successful authentication.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="Incorrect username or password",
                                           logout=True
                                           )
    return await authenticated_root_redirect(request, user.username, user.role)  # Pass role as string


@router.get("/logout", description="Logout the user and redirect to the login page.")
async def logout_user(login: bool = False):
    """
    Logout the user and redirect to the login page.

    Args:
        login (bool): Flag to determine if the user should be redirected to the login page.

    Returns:
        RedirectResponse: Redirect to the login page after logout.
    """
    if login:
        url = "/login"
    else:
        url = "/"
    response = RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)
    response = clear_tokens_in_cookies(response)
    return response
