# root.py
from fastapi import APIRouter, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import check_user
from app.auth.schemas import TokenData
from app.database.crud import get_paginated_posts, get_total_posts_count
from app.database.postgre_db import get_session
from app.tools.functions import load_unsplash_photo
from templates.icons import HI_ICON

router = APIRouter(tags=['root'])
templates = Jinja2Templates(directory="templates")


@router.get('/', description="Display the root page with paginated posts.")
async def root(request: Request,
               db: AsyncSession = Depends(get_session),
               user: TokenData | None = Depends(check_user),
               page: int = Query(1, description="Page number"),
               page_size: int = Query(21, description="Number of posts per page")):
    """
    Display the root page with paginated posts.

    Args:
        request (Request): The request object.
        db (AsyncSession): The database session.
        user (TokenData): The authenticated user data.
        page (int): The page number for pagination.
        page_size (int): The number of posts per page.

    Returns:
        TemplateResponse: The rendered HTML template with the root page content.
    """
    skip = (page - 1) * page_size
    limit = page_size

    posts = await get_paginated_posts(db, skip=skip, limit=limit)
    total_posts = await get_total_posts_count(db)

    total_pages = (total_posts + page_size - 1) // page_size

    unsplash_photo = await load_unsplash_photo('universe galaxy cosmos')
    if unsplash_photo is None:
        unsplash_photo = '/static/img/default_unsplash.jpg'

    top_message = request.session.get('top_message')
    if top_message is None:
        text = f"Hello, {user['role']} {user['username']} !" if user else "Welcome to our site!"
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
        "unsplash_photo": unsplash_photo,
        "page": page,
        "total_pages": total_pages,
        "page_size": page_size
    })
