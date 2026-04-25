from fastapi import APIRouter, Depends, HTTPException
from backend.db.models import User, Tasks, Projects, ProjectMembers
from backend.db.database import SessionLocal
from backend.api.deps import get_current_user, get_db
from backend.crud.task import create_task, get_tasks_by_project, update_task, delete_task
from backend.schemas.task import TaskResponse, TaskCreate, TaskUpdate
from typing import List

router = APIRouter()

@router.post("/{project_id}/tasks", response_model=TaskResponse)
def create_new_task(project_id: int,task_data: TaskCreate, current_user: User = Depends(get_current_user), db = Depends(get_db)):
    """Create a new task in a project."""
    project = db.query(Projects).filter(Projects.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # Check if user is a member of the project
    membership = db.query(ProjectMembers).filter(ProjectMembers.project_id == project_id, ProjectMembers.user_id == current_user.id).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    if membership.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewers cannot create tasks")
    task = create_task(project_id, task_data.title, current_user.id, db, task_data.description, task_data.priority, task_data.assigned_to, task_data.due_date)
    return task

@router.get("/{project_id}/tasks", response_model=List[TaskResponse])
def list_tasks(project_id: int, status: str = None, priority: str = None, assigned_to: int = None, current_user: User = Depends(get_current_user), db = Depends(get_db)):
    """List tasks in a project with optional filters."""
    project = db.query(Projects).filter(Projects.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # Check if user is a member of the project
    membership = db.query(ProjectMembers).filter(ProjectMembers.project_id == project_id, ProjectMembers.user_id == current_user.id).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    tasks = get_tasks_by_project(project_id, db, status, priority, assigned_to)
    return tasks

@router.put("/{project_id}/tasks/{task_id}", response_model=TaskResponse)
def update_existing_task(project_id: int, task_id: int, task_data: TaskUpdate, current_user: User = Depends(get_current_user), db = Depends(get_db)):
    """Update an existing task."""
    task = db.query(Tasks).filter(Tasks.id == task_id, Tasks.project_id == project_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # Check if user is a member of the project
    membership = db.query(ProjectMembers).filter(ProjectMembers.project_id == task.project_id, ProjectMembers.user_id == current_user.id).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    if membership.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewers cannot update tasks")
    if membership.role not in ["owner", "admin"] and task.created_by != current_user.id and task.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="Only owners, admins,task creators or assigned can update this task")
    updated_task = update_task(task_id, db, task_data.title, task_data.description, task_data.status, task_data.priority, task_data.assigned_to, task_data.due_date)
    return updated_task

@router.delete("/{project_id}/tasks/{task_id}")
def delete_existing_task(project_id: int,task_id: int, current_user: User = Depends(get_current_user), db = Depends(get_db)):
    """Delete a task."""
    task = db.query(Tasks).filter(Tasks.id == task_id, Tasks.project_id == project_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # Check if user is a member of the project
    membership = db.query(ProjectMembers).filter(ProjectMembers.project_id == task.project_id, ProjectMembers.user_id == current_user.id).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    if membership.role not in ["owner", "admin"] and task.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only owners, admins, or task creators can delete this task")
    success = delete_task(task_id, db)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete task")
    return {"message": "Task deleted successfully"}