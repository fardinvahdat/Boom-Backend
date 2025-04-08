from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from app.models import user
from sqlalchemy.orm import Session



class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"
    designer = "designer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.user)

    templates = relationship("Template", back_populates="creator")



@classmethod
async def get_by_username(cls, db: Session, username: str):
    return db.query(cls).filter(
        (cls.email == username) |
        (cls.username == username)  # Add this if you have a username field
    ).first()
