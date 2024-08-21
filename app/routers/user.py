# user.py
from fastapi import APIRouter, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import check_user
from app.auth.schemas import TokenData
from app.database.crud import (get_user_by_username,
                               get_paginated_posts_by_user,
                               get_total_posts_count_by_user,
                               create_post,
                               get_post_by_id,
                               update_post,
                               delete_post)
from app.database.postgre_db import get_session
from app.tools.functions import redirect_with_message
from templates.icons import WARNING_ICON, WARNING_CLASS, OK_ICON, OK_CLASS

router = APIRouter(tags=['user'])
templates = Jinja2Templates(directory="templates")


async def handle_top_message(request: Request):
    top_message = request.session.get('top_message')
    if top_message is not None:
        request.session.pop('top_message', None)
    return top_message


@router.get('/posts/all', description="Retrieve all posts for the authenticated user.")
async def my_posts(request: Request,
                   db: AsyncSession = Depends(get_session),
                   user: TokenData = Depends(check_user),
                   page: int = Query(1, description="Page number"),
                   page_size: int = Query(21, description="Number of posts per page")):
    """
    Retrieve all posts for the authenticated user.

    Args:
        request (Request): The request object.
        db (AsyncSession): The database session.
        user (TokenData): The authenticated user data.
        page (int): The page number for pagination.
        page_size (int): The number of posts per page.

    Returns:
        TemplateResponse: The rendered HTML template with the user's posts.
    """
    username = user['username']
    user_obj = await get_user_by_username(db, username)
    if user_obj is None:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="User not found",
                                           endpoint="/")
    user_id = user_obj.id
    skip = (page - 1) * page_size
    limit = page_size

    posts = await get_paginated_posts_by_user(db, user_id, skip=skip, limit=limit)
    total_posts = await get_total_posts_count_by_user(db, user_id)
    total_pages = (total_posts + page_size - 1) // page_size

    top_message = await handle_top_message(request)
    return templates.TemplateResponse("posts/posts.html", {
        "request": request,
        "posts": posts,
        "user": user,
        "top_message": top_message,
        "page": page,
        "total_pages": total_pages,
        "page_size": page_size
    })


@router.get('/posts/view/{post_id}', description="View a specific post by ID.")
async def view_post(request: Request, post_id: int, db: AsyncSession = Depends(get_session),
                    user: TokenData = Depends(check_user)):
    """
    View a specific post by ID.

    Args:
        request (Request): The request object.
        post_id (int): The ID of the post to view.
        db (AsyncSession): The database session.
        user (TokenData): The authenticated user data.

    Returns:
        TemplateResponse: The rendered HTML template with the post details.
    """
    post = await get_post_by_id(db, post_id)
    if not post:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="Post not found",
                                           endpoint="/")
    top_message = await handle_top_message(request)
    return templates.TemplateResponse("posts/view_post.html", {
        "request": request,
        "post": post,
        "user": user,
        "top_message": top_message
    })


@router.get('/posts/new', description="Display the form to create a new post.")
async def create_post_form(request: Request, user: TokenData = Depends(check_user)):
    """
    Display the form to create a new post.

    Args:
        request (Request): The request object.
        user (TokenData): The authenticated user data.

    Returns:
        TemplateResponse: The rendered HTML template for the new post form.
    """
    top_message = await handle_top_message(request)
    return templates.TemplateResponse("posts/create_post.html", {
        "request": request,
        "user": user,
        "top_message": top_message
    })


@router.post('/posts/new', description="Create a new post.")
async def create_post_route(request: Request, db: AsyncSession = Depends(get_session),
                            user: TokenData = Depends(check_user)):
    """
    Create a new post.

    Args:
        request (Request): The request object.
        db (AsyncSession): The database session.
        user (TokenData): The authenticated user data.

    Returns:
        RedirectResponse: Redirect to the posts list after creating the post.
    """
    form = await request.form()
    content = form.get("content")
    if not content:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="Content is required",
                                           endpoint="/posts/new")
    username = user['username']
    user_obj = await get_user_by_username(db, username)
    if user_obj is None:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="User not found",
                                           endpoint="/")
    user_id = user_obj.id
    post = await create_post(db, content, user_id)
    return await redirect_with_message(request=request,
                                       message_class=OK_CLASS,
                                       message_icon=OK_ICON,
                                       message_text="Post created successfully",
                                       endpoint="/posts/all")


@router.get('/posts/edit/{post_id}', description="Display the form to edit a post.")
async def edit_post_form(request: Request, post_id: int, db: AsyncSession = Depends(get_session),
                         user: TokenData = Depends(check_user)):
    """
    Display the form to edit a post.

    Args:
        request (Request): The request object.
        post_id (int): The ID of the post to edit.
        db (AsyncSession): The database session.
        user (TokenData): The authenticated user data.

    Returns:
        TemplateResponse: The rendered HTML template for the edit post form.
    """
    post = await get_post_by_id(db, post_id)
    if not post:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="Post not found",
                                           endpoint="/posts/all")
    username = user['username']
    user_obj = await get_user_by_username(db, username)
    if user_obj is None:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="User not found",
                                           endpoint="/")
    user_id = user_obj.id
    if post.user_id != user_id:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="You do not have permission to edit this post",
                                           endpoint="/posts/all")
    top_message = await handle_top_message(request)
    return templates.TemplateResponse("posts/edit_post.html", {
        "request": request,
        "post": post,
        "user": user,
        "top_message": top_message
    })


@router.post('/posts/edit/{post_id}', description="Update a post.")
async def edit_post_route(request: Request, post_id: int, db: AsyncSession = Depends(get_session),
                          user: TokenData = Depends(check_user)):
    """
    Update a post.

    Args:
        request (Request): The request object.
        post_id (int): The ID of the post to update.
        db (AsyncSession): The database session.
        user (TokenData): The authenticated user data.

    Returns:
        RedirectResponse: Redirect to the posts list after updating the post.
    """
    post = await get_post_by_id(db, post_id)
    if not post:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="Post not found",
                                           endpoint="/posts/all")
    username = user['username']
    user_obj = await get_user_by_username(db, username)
    if user_obj is None:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="User not found",
                                           endpoint="/")
    user_id = user_obj.id
    if post.user_id != user_id:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="You do not have permission to edit this post",
                                           endpoint="/posts/all")
    form = await request.form()
    content = form.get("content")
    if not content:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="Content is required",
                                           endpoint=f"/posts/edit/{post_id}")
    post = await update_post(db, post_id, content)
    return await redirect_with_message(request=request,
                                       message_class=OK_CLASS,
                                       message_icon=OK_ICON,
                                       message_text="Post updated successfully",
                                       endpoint="/posts/all")


@router.post('/posts/delete/{post_id}', description="Delete a post.")
async def delete_post_route(request: Request, post_id: int, db: AsyncSession = Depends(get_session),
                            user: TokenData = Depends(check_user)):
    """
    Delete a post.

    Args:
        request (Request): The request object.
        post_id (int): The ID of the post to delete.
        db (AsyncSession): The database session.
        user (TokenData): The authenticated user data.

    Returns:
        RedirectResponse: Redirect to the posts list after deleting the post.
    """
    post = await get_post_by_id(db, post_id)
    if not post:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="Post not found",
                                           endpoint="/posts/all")
    username = user['username']
    user_obj = await get_user_by_username(db, username)
    if user_obj is None:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="User not found",
                                           endpoint="/")
    user_id = user_obj.id
    if post.user_id != user_id:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="You do not have permission to delete this post",
                                           endpoint="/posts/all")
    await delete_post(db, post_id)
    return await redirect_with_message(request=request,
                                       message_class=OK_CLASS,
                                       message_icon=OK_ICON,
                                       message_text="Post deleted successfully",
                                       endpoint="/posts/all")
