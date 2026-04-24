from fastapi import APIRouter, HTTPException, Depends
from backend.db.models import User, Projects, ProjectMembers, Tasks
from backend.db.database import SessionLocal
from backend.api.deps import get_current_user, get_db
from backend.crud.project import generate_project, get_user_projects, get_project_by_id, join_project, get_member_or_403

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

@router.get("/{project_id}/members")
def list_members(project_id: int, current_user: User = Depends(get_current_user), db = Depends(get_db)):
    """List all members of a project."""
    get_member_or_403(db, project_id, current_user.id)  # Ensure user is a member
    members = db.query(ProjectMembers, User).join(User, ProjectMembers.user_id == User.id).filter(ProjectMembers.project_id == project_id).all()
    return [{"member_id": m.id, "role": m.role, "user": {"id": u.id, "username": u.username, "display_name": u.display_name}} for m, u in members]

@router.put("/{project_id}/members/{member_id}/role")
def change_member_role(project_id: int, member_id: int, new_role: str, current_user: User = Depends(get_current_user), db = Depends(get_db)):
    """Change a member's role in the project."""
    if new_role not in ["owner", "admin", "member", "viewer"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    requester = get_member_or_403(db, project_id, current_user.id)
    if requester.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only owners and admins can change roles")
    # Prevent owner from demoting themselves
    if membership.user_id == current_user.id and membership.role == "owner" and new_role != "owner":
        raise HTTPException(status_code=400, detail="Owner cannot demote themselves")
    membership = get_member_or_403(db, project_id, member_id)  # Ensure target member exists
    if membership.role == "owner" and requester.role != "owner":
        raise HTTPException(status_code=403, detail="Only owners can change the role of another owner")
    
    membership.role = new_role
    db.commit()
    db.refresh(membership)
    return {"message": "Role updated successfully", "user_id": membership.user_id, "new_role": membership.role}

@router.delete("/{project_id}/members/{member_id}")
def remove_member(project_id: int, member_id: int, current_user: User = Depends(get_current_user), db = Depends(get_db)):
    """Remove a member from the project."""
    # Check if current user is owner
    owner_membership = db.query(ProjectMembers).filter(ProjectMembers.project_id == project_id, ProjectMembers.user_id == current_user.id, ProjectMembers.role == "owner").first()
    if current_user.id != member_id:  # not removing self
        if not owner_membership:
            raise HTTPException(status_code=403, detail="Only owners can remove members")
        
    membership = db.query(ProjectMembers).filter(ProjectMembers.project_id == project_id, ProjectMembers.user_id == member_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(membership)
    db.commit()
    return {"message": "Member removed successfully"}

@router.delete("/{project_id}")
def delete_project(project_id: int, current_user: User = Depends(get_current_user), db = Depends(get_db)):
    """Delete a project."""
    # Check if current user is owner
    owner_membership = db.query(ProjectMembers).filter(ProjectMembers.project_id == project_id, ProjectMembers.user_id == current_user.id, ProjectMembers.role == "owner").first()
    if not owner_membership:
        raise HTTPException(status_code=403, detail="Only owners can delete the project")
    # Delete project
    project = db.query(Projects).filter(Projects.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.query(Tasks).filter(Tasks.project_id == project_id).delete()
    db.query(ProjectMembers).filter(ProjectMembers.project_id == project_id).delete()
    db.delete(project)  # delete project last
    db.commit()
    return {"message": "Project deleted successfully"}