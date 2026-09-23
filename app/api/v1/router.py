from fastapi import APIRouter
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import apps
from app.api.v1.endpoints import theme

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(apps.router, prefix="/apps", tags=["Apps"])
api_router.include_router(theme.router, prefix="/theme", tags=["System Event Themes"])