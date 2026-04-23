from backend.db.init_db import init_db
from backend.api.routes import auth as auth_router
from fastapi import FastAPI

init_db()

app = FastAPI()

app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])