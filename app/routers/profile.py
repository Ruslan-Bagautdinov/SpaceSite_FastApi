import os
from typing import Optional

from fastapi import (APIRouter,
                     Depends,
                     status,
                     Request,
                     Form,
                     UploadFile,
                     File)
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import check_user
from app.auth.schemas import TokenData, UserProfileUpdate
from app.config import IMAGE_DIR
from app.database.crud import (get_user,
                               get_user_profile,
                               get_user_by_username,
                               update_user_profile,
                               delete_user)
from app.database.postgre_db import get_session
from app.tools.functions import redirect_with_message
from app.tools.functions import save_upload_file, read_and_encode_photo
from templates.icons import WARNING_ICON, WARNING_CLASS, OK_ICON, OK_CLASS, USER_DELETE_ICON

router = APIRouter(tags=['user profile'], prefix='/protected')
templates = Jinja2Templates(directory="templates")


@router.get("/me")
async def get_me(request: Request,
                 db: AsyncSession = Depends(get_session),
                 user: TokenData | None = Depends(check_user)):
    user_profile = await get_user_by_username(db, user['username'])
    if user_profile:
        user_id = user_profile.id
        return RedirectResponse(f"/protected/profile/{user_id}",
                                status_code=status.HTTP_302_FOUND
                                )
    else:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="User not found",
                                           logout=True
                                           )


@router.get("/profile/{user_id}")
async def get_profile(request: Request,
                      user_id: int,
                      db: AsyncSession = Depends(get_session),
                      user: TokenData | None = Depends(check_user)
                      ):
    top_message = request.session.get('top_message')
    if top_message:
        request.session.pop('top_message', None)

    result_user = await get_user(db, user_id)
    if not result_user:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="User not found",
                                           logout=True
                                           )

    profile = {
        'user_id': result_user.id,
        'username': result_user.username,
        'email': result_user.email,
        'role': result_user.role
    }

    result_profile = await get_user_profile(db, user_id)
    if not result_profile:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="User profile not found",
                                           logout=True
                                           )

    profile_addon = {
        'first_name': result_profile.first_name,
        'last_name': result_profile.last_name,
        'phone_number': result_profile.phone_number,
        'user_age': result_profile.user_age}

    profile.update(profile_addon)

    default_avatar_path = "static/img/default_avatar.jpg"
    if result_profile.user_photo and os.path.exists(result_profile.user_photo):
        user_photo_base64 = await read_and_encode_photo(result_profile.user_photo)
        if user_photo_base64:
            profile['user_photo'] = user_photo_base64
        else:
            default_avatar_base64 = await read_and_encode_photo(default_avatar_path)
            profile['user_photo'] = default_avatar_base64
    else:
        default_avatar_base64 = await read_and_encode_photo(default_avatar_path)
        profile['user_photo'] = default_avatar_base64

    return templates.TemplateResponse("user/profile.html",
                                      {"request": request,
                                       "user": user,
                                       "profile": profile,
                                       "top_message": top_message
                                       }
                                      )


@router.post("/profile/{user_id}/update", response_model=UserProfileUpdate)
async def update_profile(request: Request,
                         user_id: int,
                         first_name: Optional[str] = Form(None),
                         last_name: Optional[str] = Form(None),
                         phone_number: Optional[str] = Form(None),
                         user_photo: Optional[UploadFile] = File(None),
                         user_age: Optional[str] = Form(None),
                         role: Optional[str] = Form(None),  # Add role parameter
                         db: AsyncSession = Depends(get_session),
                         current_user: TokenData = Depends(check_user)  # Add current_user dependency
                         ):
    user = await get_user(db, user_id)
    user_profile = await get_user_profile(db, user_id)
    if not user_profile:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="User profile not found",
                                           endpoint="/"
                                           )

    previous_photo_path = user_profile.user_photo
    if user_photo and user_photo.filename:
        if user_photo.content_type not in ['image/jpeg', 'image/png']:
            return await redirect_with_message(request=request,
                                               message_class=WARNING_CLASS,
                                               message_icon=WARNING_ICON,
                                               message_text="File must be an image!",
                                               endpoint=f"/protected/profile/{user_id}"
                                               )

        file_location = f"{IMAGE_DIR}/{user_photo.filename}"
        await save_upload_file(user_photo, file_location)

        if previous_photo_path and os.path.exists(previous_photo_path):
            os.remove(previous_photo_path)
    else:
        file_location = previous_photo_path

    if current_user['role'] == 'admin':
        user_profile = UserProfileUpdate(first_name=first_name,
                                         last_name=last_name,
                                         phone_number=phone_number,
                                         user_photo=file_location,
                                         user_age=user_age,
                                         role=role)
    else:
        user_profile = UserProfileUpdate(first_name=first_name,
                                         last_name=last_name,
                                         phone_number=phone_number,
                                         user_photo=file_location,
                                         user_age=user_age)

    await update_user_profile(db, user_id, user_profile)

    if role and current_user['role'] == 'admin':
        user.role = role
        await db.commit()
        await db.refresh(user)

    if current_user['role'] == 'admin':
        endpoint = f"/protected/profile/{user_id}"
    else:
        endpoint = "/protected/me"

    return await redirect_with_message(request=request,
                                       message_class=OK_CLASS,
                                       message_icon=OK_ICON,
                                       message_text=f"{user.username}, Your profile has been updated!",
                                       endpoint=endpoint)


@router.get("/profile/{user_id}/delete", response_class=HTMLResponse)
async def confirm_delete(request: Request,
                         user_id: int,
                         user: TokenData | None = Depends(check_user)):
    if user['role'] == 'admin':
        return await delete_user_profile(user_id, request)
    return templates.TemplateResponse("user/confirm_delete.html",
                                      {"request": request,
                                       "user_id": user_id,
                                       "user": user}
                                      )


@router.post("/profile/{user_id}/delete")
async def delete_user_profile(user_id: int,
                              request: Request,
                              db: AsyncSession = Depends(get_session),
                              user: TokenData | None = Depends(check_user)):
    user_profile = await get_user_profile(db, user_id)
    previous_photo_path = user_profile.user_photo

    if await delete_user(db, user_id):
        if previous_photo_path and os.path.exists(previous_photo_path):
            os.remove(previous_photo_path)

        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=USER_DELETE_ICON,
                                           message_text=f"{user['username']} has been deleted!",
                                           logout=True
                                           )
    else:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="User not found",
                                           logout=True
                                           )
