from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.template import TemplateCreate, TemplateOut, TemplateDetail
from app.services import template as template_service
from app.database import get_db
from app.services.auth import get_current_user
from app.models.user import User, UserRole

router = APIRouter()

@router.post("/", response_model=TemplateOut)
def create_template(
    template: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.admin, UserRole.designer]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return template_service.create_template(db, template, current_user.id)

@router.get("/", response_model=List[TemplateOut])
def list_templates(
    width: Optional[int] = None,
    height: Optional[int] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return template_service.get_templates(db, width, height, category)

@router.get("/{template_id}", response_model=TemplateDetail)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    template = template_service.get_template_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template
