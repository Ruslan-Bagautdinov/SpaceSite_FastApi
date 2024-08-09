from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from alembic.config import Config

from app.auth.middleware import check_access_token
from app.config import SECRET_KEY, BASE_DIR, DATABASE_URL
from app.routers.admin import router as admin_router
from app.routers.login import router as login_router
from app.routers.posts import router as posts_router
from app.routers.profile import router as profile_router
from app.routers.register import router as register_router
from app.routers.root import router as root_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    lifespan=lifespan,
    title="SPACE SITE!",
    description="""
    **SPACE SITE!** is a FastAPI-based demo site that takes you on a journey through the cosmos. 
    Explore beautiful space images on the home page, manage user profiles, create and edit posts, 
    and administer user data with ease. This application showcases the power and flexibility of FastAPI 
    for building modern web applications.

    ### Key Features:
    - **Stunning Space Images**: The home page features captivating images of the universe, galaxies, and cosmos, 
      sourced from Unsplash to provide an immersive experience.
    - **User Management**: Register, log in, and manage user profiles with personalized information, including 
      profile pictures and contact details.
    - **Post Creation and Editing**: Users can create, view, edit, and delete posts, making it easy to share 
      thoughts and discoveries.
    - **Admin Dashboard**: Administrators have access to an admin dashboard to manage user data and view 
      user-specific posts.
    - **Secure and Scalable**: Built with security and scalability in mind, leveraging FastAPI's robust 
      middleware and dependency injection systems.
    - **Two-Role Authentication**: Implements a secure authentication system using JWT (JSON Web Tokens) for 
      access and refresh tokens, stored in cookies to enhance security and user experience.
    - **Async Postgres Database**: Utilizes an asynchronous Postgres database for efficient and high-performance 
      data handling, ensuring smooth operations even under high load.

    Whether you're a space enthusiast, a developer exploring FastAPI, or simply looking for a beautifully 
    designed web application, SPACE SITE! offers an engaging experience.
    """,
    version="1.0.0",
)

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
app.include_router(admin_router)
