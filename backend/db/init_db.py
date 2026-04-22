from backend.db.database import engine, Base
from backend.db.models import User, Projects, ProjectMembers, Tasks, Activities

def init_db():
    Base.metadata.create_all(bind=engine)
