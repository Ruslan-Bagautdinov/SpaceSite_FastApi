from fastapi import (APIRouter,
                     Depends,
                     Request)
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgre_db import get_session
from app.routers.login import get_current_user, credentials_exception


router = APIRouter(tags=['protected'])


@router.post('/secret_place')
async def secret_place(request: Request,
                       db: AsyncSession = Depends(get_session)):

    user = await get_current_user(request, db)
    if user:
        return {"message": f"Hello {user['username']}"}
    else:
        raise credentials_exception
