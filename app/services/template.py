from sqlalchemy.orm import Session
from app.models.template import Template
from app.schemas.template import TemplateCreate


def create_template(db: Session, template_data: TemplateCreate, user_id: int):
    template = Template(**template_data.dict(), creator_id=user_id)
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def get_templates(db: Session, width: int = None, height: int = None, category: str = None):
    query = db.query(Template)
    if width:
        query = query.filter(Template.width == width)
    if height:
        query = query.filter(Template.height == height)
    if category:
        query = query.filter(Template.category == category)
    return query.all()


def get_template_by_id(db: Session, template_id: int):
    return db.query(Template).filter(Template.id == template_id).first()


def get_templates_by_user(db: Session, user_id: int):
    return db.query(Template).filter(Template.creator_id == user_id).all()
