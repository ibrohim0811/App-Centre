from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.app_model import App, AppVersion
from app.models.user import User
from app.schemas.app_schema import AppCreate, AppOut, AppVersionCreate, AppVersionOut
from app.api.v1.deps import get_current_user

router = APIRouter()


# 1. Barcha iDev ilovalari ro'yxatini olish (Mobil Do'kon oynasi uchun)
@router.get("/", response_model=list[AppOut])
async def get_all_apps(
    db: AsyncSession = Depends(get_db)
):
    stmt = select(App).where(App.is_active == True).options(selectinload(App.versions))
    result = await db.execute(stmt)
    return result.scalars().all()


# 2. Yangi ilova qo'shish (Admin/Developer uchun)
@router.post("/", response_model=AppOut, status_code=status.HTTP_201_CREATED)
async def create_app(
    app_in: AppCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Package name unikal ekanligini tekshiramiz
    stmt = select(App).where(App.package_name == app_in.package_name)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Ushbu package_name mavjud!")

    new_app = App(**app_in.model_dump())
    db.add(new_app)
    await db.commit()
    
    # Reload with empty versions
    stmt = select(App).where(App.id == new_app.id).options(selectinload(App.versions))
    result = await db.execute(stmt)
    return result.scalars().first()


# 3. Ilovaga yangi versiya qo'shish (New Release)
@router.post("/version", response_model=AppVersionOut, status_code=status.HTTP_201_CREATED)
async def add_app_version(
    version_in: AppVersionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(App).where(App.id == version_in.app_id)
    result = await db.execute(stmt)
    app = result.scalars().first()
    
    if not app:
        raise HTTPException(status_code=404, detail="Ilova topilmadi")

    new_version = AppVersion(**version_in.model_dump())
    db.add(new_version)
    await db.commit()
    await db.refresh(new_version)
    return new_version


# 4. OTA Update Check (Mobil ilovadan so'rov keladi)
@router.get("/check-update/{package_name}")
async def check_update(
    package_name: str,
    current_version_code: int,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(App).where(App.package_name == package_name, App.is_active == True)
    result = await db.execute(stmt)
    app = result.scalars().first()

    if not app:
        raise HTTPException(status_code=404, detail="Ilova topilmadi")

    # Eng oxirgi versiyani olish
    v_stmt = (
        select(AppVersion)
        .where(AppVersion.app_id == app.id)
        .order_by(AppVersion.version_code.desc())
    )
    v_result = await db.execute(v_stmt)
    latest_version = v_result.scalars().first()

    if not latest_version:
        return {"update_available": False, "message": "Versiyalar mavjud emas"}

    has_update = latest_version.version_code > current_version_code

    return {
        "update_available": has_update,
        "app_name": app.name,
        "latest_version": {
            "version_name": latest_version.version_name,
            "version_code": latest_version.version_code,
            "changelog": latest_version.changelog,
            "download_url": latest_version.download_url,
            "file_size_bytes": latest_version.file_size_bytes
        } if has_update else None
    }