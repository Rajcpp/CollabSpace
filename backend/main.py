from backend.db.init_db import init_db
from backend.api.routes import auth as auth_router
from backend.api.routes import projects as projects_router
from backend.api.routes import tasks as tasks_router
from fastapi import FastAPI

init_db()

app = FastAPI()

app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])
app.include_router(projects_router.router, prefix="/api/projects", tags=["projects"])
app.include_router(tasks_router.router, prefix="/api/projects", tags=["tasks"])