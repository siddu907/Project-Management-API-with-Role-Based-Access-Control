from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app import schemas, models
from app.utils import get_db, get_current_user, require_roles, is_project_member

router = APIRouter()

def _member_response(membership: models.ProjectMember) -> dict:
    return {
        "id": membership.id,
        "project_id": membership.project_id,
        "project_name": membership.project.name,
        "user_id": membership.user_id,
        "full_name": membership.user.full_name,
        "role": membership.user.role,
    }


@router.post("/{project_id}/members", response_model=schemas.ProjectMemberRead)
def add_member(
    project_id: int,
    membership_in: schemas.ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("Admin", "Manager")),
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if current_user.role == models.RoleEnum.manager and not is_project_member(current_user.id, project_id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    existing = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id,
        models.ProjectMember.user_id == membership_in.user_id,
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already a project member")
    membership = models.ProjectMember(project_id=project_id, user_id=membership_in.user_id)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return _member_response(membership)


@router.get("/{project_id}/members", response_model=List[schemas.ProjectMemberRead])
def list_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if current_user.role != models.RoleEnum.admin and not is_project_member(current_user.id, project_id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    memberships = db.query(models.ProjectMember).filter(models.ProjectMember.project_id == project_id).all()
    return [_member_response(membership) for membership in memberships]
