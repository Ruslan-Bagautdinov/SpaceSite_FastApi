from fastapi import (APIRouter,
                     Form,
                     Depends,
                     HTTPException,
                     status,
                     Request)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgre_db import get_session
from app.auth.schemas import UserCreate, User
from app.auth.utils import create_access_token
from app.database.crud import (create_user,
                               get_user_by_username)


router = APIRouter(tags=['user register'])
templates = Jinja2Templates(directory="templates")


@router.get('/register', response_class=HTMLResponse)
async def register_user(request: Request):
    return templates.TemplateResponse("user/register.html",
                                      {"request": request})


@router.post("/register", response_model=User)
async def register_user(username: str = Form(...),
                        email: str = Form(...),
                        password: str = Form(...),
                        db: AsyncSession = Depends(get_session)
                        ):
    db_user = await get_user_by_username(db, username=username)
    if db_user:
        raise HTTPException(status_code=400,
                            detail="Username already registered")

    user = UserCreate(username=username, email=email, password=password)

    await create_user(db=db, user=user)

    access_token = create_access_token(data={"sub": user.username})

    response = RedirectResponse(url="/",
                                status_code=status.HTTP_302_FOUND
                                )

    response.set_cookie(
        "access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=False,
        samesite='lax',
        max_age=1800,
        expires=1800,
    )
    return response
