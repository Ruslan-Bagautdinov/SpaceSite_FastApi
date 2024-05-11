from fastapi import (APIRouter,
                     Depends,
                     status,
                     Request,
                     Form,
                     UploadFile,
                     File,
                     HTTPException)
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import os


from app.auth.schemas import TokenData, UserProfileUpdate
from app.auth.middleware import check_user
from app.database.postgre_db import get_session
from app.database.crud import (get_user,
                               get_user_profile,
                               get_user_by_username,
                               update_user_profile,
                               delete_user)
from app.config import IMAGE_DIR
from app.tools.tools import save_upload_file, read_and_encode_photo

from templates.icons.icons import OK_ICON, USER_DELETE_ICON


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
    if not result_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    profile = {
        'user_id': result_user.id,
        'username': result_user.username,
        'email': result_user.email}

    result_profile = await get_user_profile(db, user_id)
    if not result_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")

    profile_addon = {
        'first_name': result_profile.first_name,
        'last_name': result_profile.last_name,
        'phone_number': result_profile.phone_number,
        'ass_size': result_profile.ass_size}

    profile.update(profile_addon)

    default_avatar_path = "static/img/default_avatar.jpg"
    if result_profile.photo and os.path.exists(result_profile.photo):
        photo_base64 = await read_and_encode_photo(result_profile.photo)
        if photo_base64:
            profile['photo'] = photo_base64
        else:
            default_avatar_base64 = await read_and_encode_photo(default_avatar_path)
            profile['photo'] = default_avatar_base64
    else:
        default_avatar_base64 = await read_and_encode_photo(default_avatar_path)
        profile['photo'] = default_avatar_base64

    return templates.TemplateResponse("user/profile.html",
                                      {"request": request,
                                       "user": user,
                                       "profile": profile}
                                      )


@router.post("/profile/{user_id}/update", response_model=UserProfileUpdate)
async def update_profile(request: Request,
                         user_id: int,
                         first_name: Optional[str] = Form(None),
                         last_name: Optional[str] = Form(None),
                         phone_number: Optional[str] = Form(None),
                         photo: Optional[UploadFile] = File(None),
                         ass_size: Optional[str] = Form(None),
                         db: AsyncSession = Depends(get_session)
                         ):
    user_profile = await get_user_profile(db, user_id)
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")

    previous_photo_path = user_profile.photo
    if photo and photo.filename:
        if photo.content_type not in ['image/jpeg', 'image/png']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image")

        file_location = f"{IMAGE_DIR}/{photo.filename}"
        await save_upload_file(photo, file_location)

        if previous_photo_path and os.path.exists(previous_photo_path):
            os.remove(previous_photo_path)
    else:
        file_location = previous_photo_path

    user_profile = UserProfileUpdate(first_name=first_name,
                                     last_name=last_name,
                                     phone_number=phone_number,
                                     photo=file_location,
                                     ass_size=ass_size)

    await update_user_profile(db, user_id, user_profile)

    new_top_message = {
        "class": "alert alert-success rounded",
        "icon": OK_ICON,
        "text": ", your data successfully registered"
    }

    request.session['top_message'] = new_top_message

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/profile/{user_id}/delete", response_class=HTMLResponse)
async def confirm_delete(request: Request,
                         user_id: int,
                         user: TokenData | None = Depends(check_user)):
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

    if await delete_user(db, user_id):
        new_top_message = {
            "class": "alert alert-danger rounded",
            "icon": USER_DELETE_ICON,
            "text": f" {user['username']} deleted successfully!"
        }

        request.session['top_message'] = new_top_message
        response = RedirectResponse(url="/logout",
                                    status_code=status.HTTP_302_FOUND)
        return response
    else:
        raise HTTPException(status_code=404, detail="User not found")
