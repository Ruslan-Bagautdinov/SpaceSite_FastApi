from fastapi import (APIRouter,
                     Depends,
                     Request)
from fastapi.templating import Jinja2Templates

from app.routers.login import check_if_logged
from app.auth.schemas import User


router = APIRouter(tags=['root'])

templates = Jinja2Templates(directory="templates")


@router.get('/')
async def root(request: Request,
               user: User | None = Depends(check_if_logged)):
    data = 'Welcome to our website!'
    return templates.TemplateResponse("root.html",
                                      {"request": request,
                                       "data": data,
                                       "user": user
                                       }
                                      )
