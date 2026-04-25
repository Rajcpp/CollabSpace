from backend.db.models import Tasks, Projects
from backend.core.enums import TaskStatus, TaskPriority

def create_task(project_id: int, title: str, created_by: int, db, description: str = None, priority: str = TaskPriority.MEDIUM.value, assigned_to: int = None, due_date = None):
    new_task = Tasks(
        project_id=project_id,
        title=title,
        description=description,
        status=TaskStatus.TODO.value,
        priority=priority,
        assigned_to=assigned_to,
        created_by=created_by,
        due_date=due_date
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

def get_tasks_by_project(project_id: int, db, status: str = None, priority: str = None, assigned_to: int = None):
    query = db.query(Tasks).filter(Tasks.project_id == project_id)
    if status:
        query = query.filter(Tasks.status == status)
    if priority:
        query = query.filter(Tasks.priority == priority)
    if assigned_to:
        query = query.filter(Tasks.assigned_to == assigned_to)
    return query.all()

def update_task(task_id: int, db, title: str = None, description: str = None, status: str = None, priority: str = None, assigned_to: int = None, due_date = None):
    task = db.query(Tasks).filter(Tasks.id == task_id).first()
    if not task:
        return None
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if status is not None:
        task.status = status
    if priority is not None:
        task.priority = priority
    if assigned_to is not None:
        task.assigned_to = assigned_to
    if due_date is not None:
        task.due_date = due_date
    db.commit()
    db.refresh(task)
    return task

def delete_task(task_id: int, db):
    task = db.query(Tasks).filter(Tasks.id == task_id).first()
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True