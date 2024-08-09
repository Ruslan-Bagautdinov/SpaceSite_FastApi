from fastapi import APIRouter, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import check_user
from app.auth.schemas import TokenData
from app.database.crud import get_all_users, get_paginated_posts_by_user, get_total_posts_count_by_user
from app.database.postgre_db import get_session

router = APIRouter(tags=['admin'], prefix='/admin')
templates = Jinja2Templates(directory="templates")


@router.get("/users")
async def admin_users(request: Request,
                      db: AsyncSession = Depends(get_session),
                      user: TokenData = Depends(check_user)):
    if user['role'] != 'admin':
        return templates.TemplateResponse("error.html", {"request": request,
                                                         "error_message": "You are not authorized to view this page."})

    users = await get_all_users(db)
    return templates.TemplateResponse("admin/users.html", {"request": request, "users": users, "user": user})


@router.get("/users/{user_id}/posts")
async def admin_user_posts(request: Request,
                           user_id: int,
                           db: AsyncSession = Depends(get_session),
                           user: TokenData = Depends(check_user),
                           page: int = Query(1, description="Page number"),
                           page_size: int = Query(15, description="Number of posts per page")):
    if user['role'] != 'admin':
        return templates.TemplateResponse("error.html", {"request": request,
                                                         "error_message": "You are not authorized to view this page."})

    skip = (page - 1) * page_size
    limit = page_size

    posts = await get_paginated_posts_by_user(db, user_id, skip=skip, limit=limit)
    total_posts = await get_total_posts_count_by_user(db, user_id)
    total_pages = (total_posts + page_size - 1) // page_size

    return templates.TemplateResponse("admin/user_posts.html", {
        "request": request,
        "posts": posts,
        "user": user,
        "page": page,
        "total_pages": total_pages,
        "page_size": page_size
    })
