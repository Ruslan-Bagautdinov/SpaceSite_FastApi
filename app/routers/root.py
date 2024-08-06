from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.middleware import check_user
from app.auth.schemas import TokenData
from app.database.postgre_db import get_session
from app.tools.functions import load_unsplash_photo
from app.database.models import Post
from templates.icons import HI_ICON

router = APIRouter(tags=['root'])
templates = Jinja2Templates(directory="templates")


@router.get('/')
async def root(request: Request, db: AsyncSession = Depends(get_session), user: TokenData | None = Depends(check_user)):
    query = select(Post).order_by(Post.created_at.desc())
    result = await db.execute(query)
    posts = result.scalars().all()
    unsplash_photo = await load_unsplash_photo('universe galaxy cosmos')
    if unsplash_photo is None:
        unsplash_photo = '/static/img/default_unsplash.jpg'

    top_message = request.session.get('top_message')
    if top_message is None:
        text = f"Hello, {user['username']}!" if user else "Welcome to our site!"
        top_message = {
            "class": "alert alert-light rounded",
            "icon": HI_ICON,
            "text": text
        }
    else:
        request.session.pop('top_message', None)

    return templates.TemplateResponse("root.html", {
        "request": request,
        "user": user,
        "top_message": top_message,
        "posts": posts,
        "unsplash_photo": unsplash_photo
    })
