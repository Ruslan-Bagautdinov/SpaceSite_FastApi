from typing import Optional

from fastapi import (APIRouter,
                     Depends,
                     HTTPException,
                     status,
                     Request,
                     Form)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


from sqlalchemy.ext.asyncio import AsyncSession


from app.database.postgre_db import get_session
from app.database.crud import (get_user,
                               get_user_by_username,
                               update_user_profile)

from app.routers.login import check_user
from app.auth.schemas import TokenData, User, UserProfileUpdate


router = APIRouter(tags=['user profile'])
templates = Jinja2Templates(directory="templates")


def no_access():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Please log in to access this page",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.get("/me")
async def get_me(db: AsyncSession = Depends(get_session),
                 user: TokenData | None = Depends(check_user)):

    if user is None:
        no_access()
    else:
        user_profile = await get_user_by_username(db, user['username'])
        user_id = user_profile.id
        return RedirectResponse(f"/profile/{user_id}",
                                status_code=status.HTTP_302_FOUND
                                )


@router.get("/profile/{user_id}")
async def get_profile(request: Request,
                      user_id: int,
                      db: AsyncSession = Depends(get_session),
                      user: TokenData | None = Depends(check_user)
                      ):

    if user is None:
        no_access()
    else:
        result = await get_user(db, user_id)
        profile = {
            'username': result.username,
            'email': result.email,
            'first_name': result.first_name,
            'last_name': result.last_name,
            'photo': result.photo,
            'phone_number': result.phone_number,
            'ass_size': result.ass_size,
            'user_id': user_id,
        }
        return templates.TemplateResponse("user/profile.html",
                                          {"request": request,
                                           "user": user,
                                           "profile": profile}
                                          )


@router.post("/profile/{user_id}/update", response_model=UserProfileUpdate)
async def register_user(user_id: int,
                        request: Request,
                        first_name: Optional[str] = Form(None),
                        last_name: Optional[str] = Form(None),
                        phone_number: Optional[str] = Form(None),
                        photo: Optional[str] = Form(None),
                        ass_size: Optional[str] = Form(None),
                        db: AsyncSession = Depends(get_session),
                        user: User | None = Depends(check_user)
                        ):

    if user is None:
        no_access()
    else:
        user_id = user_id
        user_profile = UserProfileUpdate(first_name=first_name,
                                         last_name=last_name,
                                         phone_number=phone_number,
                                         photo=photo,
                                         ass_size=ass_size)

        await update_user_profile(db, user_id, user_profile)

        top_message = 'your data successfully registered'
        return templates.TemplateResponse("root.html",
                                          {"request": request,
                                           "top_message": top_message,
                                           "user": user
                                           }
                                          )
