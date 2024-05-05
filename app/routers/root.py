from fastapi import (APIRouter,
                     Depends,
                     Request)
from fastapi.templating import Jinja2Templates

from app.routers.login import check_if_logged
from app.auth.schemas import TokenData


router = APIRouter(tags=['root'])

templates = Jinja2Templates(directory="templates")


@router.get('/')
async def root(request: Request,
               user: TokenData | None = Depends(check_if_logged)):
    top_message = 'welcome to our website'
    return templates.TemplateResponse("root.html",
                                      {"request": request,
                                       "top_message": top_message,
                                       "user": user
                                       }
                                      )
