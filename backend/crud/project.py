import random
import string
from datetime import datetime
from backend.db.database import SessionLocal
from backend.db.models import Projects, ProjectMembers
from fastapi import HTTPException, Depends
from backend.api.deps import get_db

def generate_project_code(project_name: str, db) -> str:  # just pass db normally
    """
    Generate unique project code like: LAUNCH-2024, DESIGN-2024
    
    Format: {WORD}-{YEAR}-{RANDOM}
    Example: LAUNCH-2024-A7F3
    """
    # Extract first word from project name (max 8 chars)
    first_word = project_name.split()[0][:8].upper()
    
    # Get current year
    year = datetime.now().year
    
    # Generate random suffix (4 chars)
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    code = f"{first_word}-{year}-{suffix}"
    
    # Check if code exists in database, regenerate if duplicate
    while db.query(Projects).filter(Projects.project_code == code).first():
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        code = f"{first_word}-{year}-{suffix}"
    
    return code

# Alternative: Simple memorable codes
ADJECTIVES = ['swift', 'bright', 'brave', 'clever', 'bold']
NOUNS = ['falcon', 'tiger', 'dragon', 'phoenix', 'lion']

def generate_memorable_code() -> str:
    """Generate codes like: SWIFT-FALCON-2024"""
    adj = random.choice(ADJECTIVES).upper()
    noun = random.choice(NOUNS).upper()
    year = datetime.now().year
    return f"{adj}-{noun}-{year}"

def generate_project(name: str, description: str, access_type: str, user_id: int, db):
    """Create a new project with a unique code."""
    code = generate_project_code(name, db)  # pass db to generate_project_code
    new_project = Projects(
        name=name,
        description=description,
        project_code=code,
        access_type=access_type,
        created_by=user_id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    new_member = ProjectMembers(
        project_id=new_project.id,
        user_id=user_id,
        role="owner"
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_project

def get_user_projects(user_id: int, db):
    return db.query(Projects).join(ProjectMembers).filter(ProjectMembers.user_id == user_id).all()

def get_project_by_id(project_id: int, db):
    """Get a project by its ID."""
    return db.query(Projects).filter(Projects.id == project_id).first()

def join_project(db, project_code: str, user_id: int):
    # Find project by code
    project = db.query(Projects).filter(Projects.project_code == project_code).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user is already a member
    existing = db.query(ProjectMembers).filter(
        ProjectMembers.project_id == project.id,
        ProjectMembers.user_id == user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already a member of this project")
    
    # Add as member
    new_member = ProjectMembers(
        project_id=project.id,
        user_id=user_id,
        role="member"
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return {"project": project, "role": new_member.role, "joined_at": new_member.joined_at}