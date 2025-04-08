from pydantic import BaseModel
from typing import Optional


class TemplateBase(BaseModel):
    title: str
    category: str
    width: int
    height: int
    image: Optional[str]


class TemplateCreate(TemplateBase):
    json: str


class TemplateOut(TemplateBase):
    id: int
    creator_id: int

    class Config:
        orm_mode = True


class TemplateDetail(TemplateOut):
    json: str
