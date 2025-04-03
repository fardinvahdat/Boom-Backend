from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base
from sqlalchemy.orm import  Session


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)
    google_id = Column(String, nullable=True)


@classmethod
async def get_by_username(cls, db: Session, username: str):
    return db.query(cls).filter(
        (cls.email == username) |
        (cls.username == username)  # Add this if you have a username field
    ).first()
