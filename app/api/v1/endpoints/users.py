from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserInDB, UserBase
from app.models.user import User
from app.database import get_db
from app.utils.security import get_password_hash
from app.services.auth import get_current_user
from app.services import template as template_service



router = APIRouter()


@router.post("/", response_model=UserInDB)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=user.role or "user"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserBase)
def read_users_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_data = UserBase.from_orm(current_user)
    user_data.templates = template_service.get_templates_by_user(
        db, current_user.id)
    return user_data
