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

from app.database.postgre_db import get_session
from app.auth.schemas import TokenData
from app.database.crud import (authenticate_user)
from app.auth.utils import (create_access_token,
                            create_refresh_token,
                            authenticated_root_redirect)
from app.auth.middleware import check_user

router = APIRouter(tags=['user login'])

templates = Jinja2Templates(directory="templates")


# async def check_user(request: Request):
#     access_token = request.cookies.get("access_token")
#
#     if access_token is None:
#         return None
#     try:
#         payload = decode_token(access_token)
#         username: str = payload.get("sub")
#         if username is None:
#             return None
#         else:
#             return {'username': username}
#     except PyJWTError:
#         return None


# async def get_current_user(request: Request,
#                            db: AsyncSession = Depends(get_session)):
#
#     cookie_sub = await check_user(request)
#     username = cookie_sub.get('username')
#
#     if cookie_sub:
#
#         user = await get_user_by_username(db, username=username)
#         if user is None:
#             return None
#
#         # user_data = await get_user(db, user.id)
#         return user
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Please log in to access this page",
#             headers={"WWW-Authenticate": "Bearer"},
#         )


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
    # access_token = create_access_token(user.username)
    # refresh_token = create_refresh_token(user.username)
    #
    # response = RedirectResponse(url="/",
    #                             status_code=status.HTTP_302_FOUND
    #                             )
    #
    # response.set_cookie(
    #     "access_token",
    #     value=f"Bearer {access_token}",
    #     httponly=True,
    #     secure=False,
    #     samesite='lax'
    # )
    #
    # response.set_cookie(
    #     "refresh_token",
    #     value=f"Bearer {refresh_token}",
    #     httponly=True,
    #     secure=False,
    #     samesite='lax'
    # )
    # return response

    return authenticated_root_redirect(user.username)


@router.get("/logout")
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return RedirectResponse(url="/",
                            status_code=status.HTTP_302_FOUND,
                            headers={"Set-Cookie": "access_token=; "
                                                   "Path=/; "
                                                   "Expires=Thu, 01 Jan 1970 00:00:00 GMT"
                                     }
                            )
