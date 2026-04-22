from sqlalchemy import Column, Integer, String, Text, ForeignKey
from datetime import datetime
from sqlalchemy import DateTime, JSON
from sqlalchemy.orm import Mapped, relationship, UniqueConstraint
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    display_name = Column(String)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Projects(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    project_code = Column(String, unique=True, index=True)
    access_type = Column(String) # public or private or invite-only
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProjectMembers(Base):
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String) # owner, admin, member, viewer
    joined_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('project_id', 'user_id'),)

class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String)
    description = Column(Text)
    status = Column(String) # todo, in-progress, review, done
    
    priority = Column(String) # low, medium, high, urgent
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Activities(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    action_type = Column(String) # task_created, task_updated, task_completed, user_joined, user_left
    entity_type = Column(String) # task, project, member
    entity_id = Column(Integer) # id of the task, project or member involved in the activity
    activity_data = Column(JSON) # JSON string with additional info about the activity
    created_at = Column(DateTime, default=datetime.utcnow)
