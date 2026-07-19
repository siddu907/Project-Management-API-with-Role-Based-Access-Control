from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session
from app import schemas, models
from app.utils import get_db, get_current_user, require_roles, is_project_member

router = APIRouter()

def _project_response(project: models.Project) -> dict:
    return {
        "id": project.id,
        "project_id": project.id,
        "project_name": project.name,
        "project_description": project.description,
        "created_at": project.created_at,
        "is_deleted": project.is_deleted,
        "created_by_user": {
            "user_id": project.creator.id,
            "full_name": project.creator.full_name,
            "role": project.creator.role,
        },
    }


def _task_response(task: models.Task) -> dict:
    return {
        "id": task.id,
        "task_id": task.id,
        "project_id": task.project_id,
        "project_name": task.project.name,
        "title": task.title,
        "task_title": task.title,
        "description": task.description,
        "task_description": task.description,
        "status": task.status,
        "priority": task.priority,
        "due_date": task.due_date,
        "assigned_to_user": {
            "user_id": task.assignee.id,
            "full_name": task.assignee.full_name,
            "role": task.assignee.role,
        } if task.assigned_to else None,
        "is_deleted": task.is_deleted,
    }


@router.post("/", response_model=schemas.TaskRead)
def create_task(
    task_in: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("Admin", "Manager")),
):
    project = db.query(models.Project).filter(models.Project.id == task_in.project_id, models.Project.is_deleted == False).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if current_user.role == models.RoleEnum.manager and not is_project_member(current_user.id, task_in.project_id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    if task_in.assigned_to is not None:
        assignee = db.query(models.User).filter(models.User.id == task_in.assigned_to).first()
        if not assignee:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assigned user not found")
    task = models.Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        priority=task_in.priority,
        due_date=task_in.due_date,
        assigned_to=task_in.assigned_to,
        project_id=task_in.project_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_response(task)

@router.get("/", response_model=List[schemas.TaskRead])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    assigned_to: Optional[int] = Query(None),
    project_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    query = db.query(models.Task).filter(models.Task.is_deleted == False)
    if current_user.role == models.RoleEnum.admin:
        pass
    elif current_user.role == models.RoleEnum.manager:
        project_ids = [membership.project_id for membership in current_user.memberships]
        query = query.filter(models.Task.project_id.in_(project_ids))
    else:
        query = query.filter(models.Task.assigned_to == current_user.id)
    if assigned_to is not None:
        query = query.filter(models.Task.assigned_to == assigned_to)
    if project_id is not None:
        query = query.filter(models.Task.project_id == project_id)
    tasks = query.offset((page - 1) * page_size).limit(page_size).all()
    return [_task_response(task) for task in tasks]

@router.get("/{task_id}", response_model=schemas.TaskRead)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.is_deleted == False).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if current_user.role == models.RoleEnum.admin:
        return _task_response(task)
    if task.assigned_to == current_user.id or is_project_member(current_user.id, task.project_id, db):
        return _task_response(task)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

@router.put("/{task_id}", response_model=schemas.TaskRead)
def update_task(
    task_id: int,
    task_in: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.is_deleted == False).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if current_user.role == models.RoleEnum.member:
        if task.assigned_to != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        invalid_changes = any([
            task_in.title is not None,
            task_in.description is not None,
            task_in.due_date is not None,
            task_in.assigned_to is not None,
        ])
        if invalid_changes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Members can only update task status or priority")
        if task_in.status is None and task_in.priority is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Members must update task status or priority")
        if task_in.status is not None:
            task.status = task_in.status
        if task_in.priority is not None:
            task.priority = task_in.priority
    else:
        if current_user.role == models.RoleEnum.manager and not is_project_member(current_user.id, task.project_id, db):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        if task_in.title is not None:
            task.title = task_in.title
        if task_in.description is not None:
            task.description = task_in.description
        if task_in.status is not None:
            task.status = task_in.status
        if task_in.priority is not None:
            task.priority = task_in.priority
        if task_in.due_date is not None:
            task.due_date = task_in.due_date
        if task_in.assigned_to is not None:
            assignee = db.query(models.User).filter(models.User.id == task_in.assigned_to).first()
            if not assignee:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assigned user not found")
            task.assigned_to = task_in.assigned_to
    db.commit()
    db.refresh(task)
    return _task_response(task)

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("Admin", "Manager")),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if current_user.role == models.RoleEnum.manager and not is_project_member(current_user.id, task.project_id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    task.is_deleted = True
    db.commit()
    return {"detail": "Task deleted"}
