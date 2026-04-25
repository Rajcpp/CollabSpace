from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from backend.schemas.user import UserBrief

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    access_type: str = "private"

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    project_code: str
    access_type: str
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True

class MemberResponse(BaseModel):
    member_id: int
    role: str
    user: UserBrief

    class Config:
        from_attributes = True