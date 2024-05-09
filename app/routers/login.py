from fastapi import (APIRouter,
                     Depends,
                     HTTPException,
                     status,
                     Request)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgre_db import get_session
from app.auth.schemas import TokenData
from app.database.crud import (authenticate_user)
from app.auth.utils import (authenticated_root_redirect,
                            clear_tokens_in_cookies)
from app.auth.middleware import check_user

router = APIRouter(tags=['user login'])

templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request,
                    user: TokenData | None = Depends(check_user)):
    return templates.TemplateResponse("user/login.html",
                                      {"request": request,
                                       "user": user})


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

    return await authenticated_root_redirect(user.username)


@router.get("/logout")
async def logout_user():

    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response = clear_tokens_in_cookies(response)

    return response
