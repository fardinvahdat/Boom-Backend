from fastapi import APIRouter
from app.api.v1.endpoints import auth_router, users_router, images_router, templates_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(images_router, prefix="/images", tags=["images"])
api_router.include_router(
    templates_router, prefix="/templates", tags=["templates"])
