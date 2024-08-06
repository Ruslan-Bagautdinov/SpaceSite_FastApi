from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import check_user
from app.auth.schemas import TokenData
from app.database.crud import (get_user_by_username,
                               get_posts_by_user,
                               create_post,
                               get_post_by_id,
                               update_post,
                               delete_post)
from app.database.postgre_db import get_session
from app.tools.functions import redirect_with_message
from templates.icons import WARNING_ICON, WARNING_CLASS, OK_ICON, OK_CLASS

router = APIRouter(tags=['posts'])
templates = Jinja2Templates(directory="templates")


@router.get('/posts')
async def my_posts(request: Request, db: AsyncSession = Depends(get_session), user: TokenData = Depends(check_user)):
    username = user['username']
    user_obj = await get_user_by_username(db, username)
    if user_obj is None:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="User not found",
                                           endpoint="/")
    user_id = user_obj.id
    posts = await get_posts_by_user(db, user_id)
    return templates.TemplateResponse("user/my_posts.html", {"request": request, "posts": posts, "user": user})


@router.get('/posts/create')
async def create_post_form(request: Request, user: TokenData = Depends(check_user)):
    return templates.TemplateResponse("user/create_post.html", {"request": request, "user": user})


@router.post('/posts/create')
async def create_post_route(request: Request, db: AsyncSession = Depends(get_session),
                            user: TokenData = Depends(check_user)):
    form = await request.form()
    content = form.get("content")
    if not content:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="Content is required",
                                           endpoint="/posts/create")
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
                                       endpoint="/posts")


@router.get('/posts/{post_id}/edit')
async def edit_post_form(request: Request, post_id: int, db: AsyncSession = Depends(get_session),
                         user: TokenData = Depends(check_user)):
    post = await get_post_by_id(db, post_id)
    if not post:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="Post not found",
                                           endpoint="/posts")
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
                                           endpoint="/posts")
    return templates.TemplateResponse("user/edit_post.html", {"request": request, "post": post, "user": user})


@router.post('/posts/{post_id}/edit')
async def edit_post_route(request: Request, post_id: int, db: AsyncSession = Depends(get_session),
                          user: TokenData = Depends(check_user)):
    post = await get_post_by_id(db, post_id)
    if not post:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="Post not found",
                                           endpoint="/posts")
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
                                           endpoint="/posts")
    form = await request.form()
    content = form.get("content")
    if not content:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="Content is required",
                                           endpoint=f"/posts/{post_id}/edit")
    post = await update_post(db, post_id, content)
    return await redirect_with_message(request=request,
                                       message_class=OK_CLASS,
                                       message_icon=OK_ICON,
                                       message_text="Post updated successfully",
                                       endpoint="/posts")


@router.post('/posts/{post_id}/delete')
async def delete_post_route(request: Request, post_id: int, db: AsyncSession = Depends(get_session),
                            user: TokenData = Depends(check_user)):
    post = await get_post_by_id(db, post_id)
    if not post:
        return await redirect_with_message(request=request,
                                           message_class=WARNING_CLASS,
                                           message_icon=WARNING_ICON,
                                           message_text="Post not found",
                                           endpoint="/posts")
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
                                           endpoint="/posts")
    await delete_post(db, post_id)
    return await redirect_with_message(request=request,
                                       message_class=OK_CLASS,
                                       message_icon=OK_ICON,
                                       message_text="Post deleted successfully",
                                       endpoint="/posts")
