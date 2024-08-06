from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from alembic.config import Config

from app.routers.root import router as root_router
from app.routers.register import router as register_router
from app.routers.login import router as login_router
from app.routers.profile import router as profile_router
from app.routers.posts import router as posts_router
from app.auth.middleware import check_access_token
from app.tools.functions import perform_migrations

from app.config import SECRET_KEY, BASE_DIR, DATABASE_URL

@asynccontextmanager
async def lifespan(app: FastAPI):
    perform_migrations()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.middleware("http")(check_access_token)

templates = Jinja2Templates(directory=f"{BASE_DIR}/templates")
app.mount("/static", StaticFiles(directory=f"{BASE_DIR}/static"), name="static")

alembic_config = Config('alembic.ini')
alembic_config.set_main_option('sqlalchemy.url', DATABASE_URL)

app.include_router(root_router)
app.include_router(register_router)
app.include_router(login_router)
app.include_router(profile_router)
app.include_router(posts_router)
