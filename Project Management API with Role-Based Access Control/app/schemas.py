from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr
from app.models import RoleEnum, StatusEnum, PriorityEnum

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[RoleEnum] = None

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: RoleEnum

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[RoleEnum] = None

class UserInfo(BaseModel):
    user_id: int
    full_name: str
    role: RoleEnum

    model_config = ConfigDict(from_attributes=True)

class UserRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: RoleEnum

    model_config = ConfigDict(from_attributes=True)

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class ProjectRead(BaseModel):
    
    project_id: int
    project_name: str
    project_description: Optional[str] = None
    created_at: datetime
    created_by_user: UserInfo

    model_config = ConfigDict(from_attributes=True)

class ProjectDetailRead(BaseModel):
    project_id: int
    project_name: str
    project_description: Optional[str] = None
    created_by_user: UserInfo
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProjectMemberCreate(BaseModel):
    user_id: int

class ProjectMemberRead(BaseModel):
    project_id: int
    project_name: str
    user_id: int
    full_name: str
    role: RoleEnum

    model_config = ConfigDict(from_attributes=True)

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[StatusEnum] = StatusEnum.pending
    priority: Optional[PriorityEnum] = PriorityEnum.medium
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None
    project_id: int

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[StatusEnum] = None
    priority: Optional[PriorityEnum] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None


class TaskRead(BaseModel):
    task_id: int
    task_title: str
    project_id: int
    project_name: str
    task_title: str
    task_description: Optional[str] = None

    status: StatusEnum
    priority: PriorityEnum
    due_date: Optional[datetime] = None
    assigned_to_user: Optional[UserInfo] = None
    

    model_config = ConfigDict(from_attributes=True)

