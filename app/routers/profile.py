from fastapi import (APIRouter,
                     Depends,
                     status,
                     Request,
                     Form)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession


from app.auth.schemas import TokenData, User, UserProfileUpdate
from app.auth.middleware import check_user
from app.database.postgre_db import get_session
from app.database.crud import (get_user,
                               get_user_profile,
                               get_user_by_username,
                               update_user_profile)

from templates.icons.icons import OK_ICON


router = APIRouter(tags=['user profile'], prefix='/protected')
templates = Jinja2Templates(directory="templates")


@router.get("/me")
async def get_me(db: AsyncSession = Depends(get_session),
                 user: TokenData | None = Depends(check_user)):

    user_profile = await get_user_by_username(db, user['username'])
    user_id = user_profile.id
    return RedirectResponse(f"/protected/profile/{user_id}",
                            status_code=status.HTTP_302_FOUND
                            )


@router.get("/profile/{user_id}")
async def get_profile(request: Request,
                      user_id: int,
                      db: AsyncSession = Depends(get_session),
                      user: TokenData | None = Depends(check_user)
                      ):
    result_user = await get_user(db, user_id)

    profile = {
        'user_id': result_user.id,
        'username': result_user.username,
        'email': result_user.email}

    result_profile = await get_user_profile(db, user_id)

    profile_addon = {
        'first_name': result_profile.first_name,
        'last_name': result_profile.last_name,
        'photo': result_profile.photo,
        'phone_number': result_profile.phone_number,
        'ass_size': result_profile.ass_size}

    profile.update(profile_addon)

    return templates.TemplateResponse("user/profile.html",
                                      {"request": request,
                                       "user": user,
                                       "profile": profile}
                                      )


@router.post("/profile/{user_id}/update", response_model=UserProfileUpdate)
async def update_profile(user_id: int,
                         request: Request,
                         first_name: Optional[str] = Form(None),
                         last_name: Optional[str] = Form(None),
                         phone_number: Optional[str] = Form(None),
                         photo: Optional[str] = Form(None),
                         ass_size: Optional[str] = Form(None),
                         db: AsyncSession = Depends(get_session)
                         ):

    user_id = user_id
    user_profile = UserProfileUpdate(first_name=first_name,
                                     last_name=last_name,
                                     phone_number=phone_number,
                                     photo=photo,
                                     ass_size=ass_size)

    await update_user_profile(db, user_id, user_profile)

    new_top_message = {
        "class": "alert alert-success rounded",
        "icon": OK_ICON,
        "text": "your data successfully registered"
    }

    request.session['top_message'] = new_top_message

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
