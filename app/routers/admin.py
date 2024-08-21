# admin.py
from fastapi import APIRouter, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import check_user
from app.auth.schemas import TokenData
from app.database.crud import get_all_users, get_paginated_posts_by_user, get_total_posts_count_by_user
from app.database.postgre_db import get_session
from app.tools.functions import redirect_with_message
from templates.icons import WARNING_ICON, WARNING_CLASS

router = APIRouter(tags=['admin'], prefix='/admin')
templates = Jinja2Templates(directory="templates")


@router.get("/users", description="Retrieve a list of all users for admin view.")
async def admin_users(request: Request,
                      db: AsyncSession = Depends(get_session),
                      user: TokenData = Depends(check_user)):
    """
    Retrieve a list of all users for admin view.

    Args:
        request (Request): The request object.
        db (AsyncSession): The database session.
        user (TokenData): The authenticated user data.

    Returns:
        TemplateResponse: The rendered HTML template with the list of users.
    """
    if user['role'] != 'admin':
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="You are not authorized to view this page.",
                                           endpoint="/")

    users = await get_all_users(db)
    return templates.TemplateResponse("admin/users.html", {"request": request, "users": users, "user": user})


@router.get("/users/{user_id}/posts", description="Retrieve posts by a specific user for admin view.")
async def admin_user_posts(request: Request,
                           user_id: int,
                           db: AsyncSession = Depends(get_session),
                           user: TokenData = Depends(check_user),
                           page: int = Query(1, description="Page number"),
                           page_size: int = Query(15, description="Number of posts per page")):
    """
    Retrieve posts by a specific user for admin view.

    Args:
        request (Request): The request object.
        user_id (int): The ID of the user whose posts are to be retrieved.
        db (AsyncSession): The database session.
        user (TokenData): The authenticated user data.
        page (int): The page number for pagination.
        page_size (int): The number of posts per page.

    Returns:
        TemplateResponse: The rendered HTML template with the user's posts.
    """
    if user['role'] != 'admin':
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="You are not authorized to view this page.",
                                           endpoint="/")

    skip = (page - 1) * page_size
    limit = page_size

    posts = await get_paginated_posts_by_user(db, user_id, skip=skip, limit=limit)
    total_posts = await get_total_posts_count_by_user(db, user_id)
    total_pages = (total_posts + page_size - 1) // page_size

    return templates.TemplateResponse("posts/posts.html", {
        "request": request,
        "posts": posts,
        "user": user,
        "page": page,
        "total_pages": total_pages,
        "page_size": page_size
    })
