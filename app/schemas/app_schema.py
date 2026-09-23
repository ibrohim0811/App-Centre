from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Versiya yaratish
class AppVersionCreate(BaseModel):
    app_id: str
    version_code: int
    version_name: str
    changelog: Optional[str] = None
    download_url: str
    file_size_bytes: Optional[int] = None
    min_os_version: Optional[str] = None


class AppVersionOut(BaseModel):
    id: str
    version_code: int
    version_name: str
    changelog: Optional[str]
    download_url: str
    file_size_bytes: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# Ilova yaratish
class AppCreate(BaseModel):
    name: str
    package_name: str  # com.idev.appname
    description: Optional[str] = None
    icon_url: Optional[str] = None
    category: Optional[str] = None


class AppOut(BaseModel):
    id: str
    name: str
    package_name: str
    description: Optional[str]
    icon_url: Optional[str]
    category: Optional[str]
    is_active: bool
    created_at: datetime
    versions: List[AppVersionOut] = []

    class Config:
        from_attributes = True