from fastapi import (APIRouter,
                     Depends,
                     Request)
from fastapi.templating import Jinja2Templates

from app.routers.login import check_user
from app.auth.schemas import TokenData
from app.tools.tools import load_unsplash_photo
from templates.icons.icons import HI_ICON


router = APIRouter(tags=['root'])

templates = Jinja2Templates(directory="templates")


@router.get('/')
async def root(request: Request,
               user: TokenData | None = Depends(check_user)):

    top_message = request.session.get('top_message')
    if top_message is None:
        top_message = {
            "class": "alert alert-light rounded",
            "icon": HI_ICON,
            "text": ", welcome to our website!"
        }
    else:
        request.session.pop('top_message', None)

    unsplash_photo = await load_unsplash_photo('universe galaxy cosmos')
    if unsplash_photo is None:
        unsplash_photo = '/static/img/default_unsplash.jpg'

    return templates.TemplateResponse("root.html",
                                      {"request": request,
                                       "top_message": top_message,
                                       "unsplash_photo": unsplash_photo,
                                       "user": user
                                       }
                                      )
