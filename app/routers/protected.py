from fastapi import (APIRouter,
                     status,
                     Depends,
                     Request,
                     HTTPException)
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgre_db import get_session
from app.routers.login import get_current_user


router = APIRouter(tags=['protected'])


@router.post('/secret_place')
async def secret_place(request: Request,
                       db: AsyncSession = Depends(get_session)):

    user = await get_current_user(request, db)
    if user:
        return {"message": f"Hello {user['username']}"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please log in to access this page",
            headers={"WWW-Authenticate": "Bearer"},
        )
