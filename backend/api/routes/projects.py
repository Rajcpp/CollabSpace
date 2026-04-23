from fastapi import APIRouter, HTTPException, Depends
from backend.db.models import User, Projects, ProjectMembers
from backend.db.database import SessionLocal
from backend.api.deps import get_current_user, get_db
from backend.crud.project import generate_project, get_user_projects, get_project_by_id, join_project

router = APIRouter()

@router.post("/")
def create_project(name: str, description: str, access_type: str, current_user: User = Depends(get_current_user), db = Depends(get_db)):
    """Create a new project."""
    if access_type not in ["public", "private"]:
        raise HTTPException(status_code=400, detail="Invalid access type")
    project = generate_project(name, description, access_type, current_user.id, db)
    return {"project_id": project.id, "project_code": project.project_code}

@router.get("/")
def list_projects(current_user: User = Depends(get_current_user), db = Depends(get_db)):
    """List all projects owned by the current user."""
    projects = get_user_projects(current_user.id, db)
    return [{"id": p.id, "name": p.name, "project_code": p.project_code} for p in projects]

@router.get("/{project_id}")
def get_project(project_id: int, current_user: User = Depends(get_current_user), db = Depends(get_db)):
    """Get project details by ID."""
    project = get_project_by_id(project_id, db)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # Check if user is a member of the project
    membership = db.query(ProjectMembers).filter(ProjectMembers.project_id == project_id, ProjectMembers.user_id == current_user.id).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    return {"id": project.id, "name": project.name, "description": project.description, "project_code": project.project_code}

@router.post("/join")
def join(project_code: str, current_user: User = Depends(get_current_user), db = Depends(get_db)):
    return join_project(db, project_code, current_user.id)