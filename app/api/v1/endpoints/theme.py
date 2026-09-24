from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional

from app.core.database import get_db
from app.models.theme_model import SystemTheme
from app.models.user import User
from app.schemas.theme_schema import SystemThemeCreate, SystemThemeOut
from app.api.v1.deps import get_current_user

router = APIRouter()


# 1. Mobil ilova uchun: Hozirgi aktiv Event / Theme ni olish (Public)
@router.get("/active", response_model=Optional[SystemThemeOut])
async def get_active_theme(db: AsyncSession = Depends(get_db)):
    """Mobil ilova har gal ishga tushganda aktiv eventni tekshiradi (Masalan: Snowfalling)"""
    stmt = select(SystemTheme).where(SystemTheme.is_active == True)
    result = await db.execute(stmt)
    return result.scalars().first()


# 2. Admin Panel uchun: Yangi Event/Mavzu yaratish
@router.post(
    "/", response_model=SystemThemeOut, status_code=status.HTTP_201_CREATED
)
async def create_theme(
    theme_in: SystemThemeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_theme = SystemTheme(**theme_in.model_dump())
    db.add(new_theme)
    await db.commit()
    await db.refresh(new_theme)
    return new_theme


# 3. Admin Panel uchun: Muayyan mavzuni Aktivlashtirish (masalan: Snowfalling ni set qilish)
@router.post("/{theme_id}/activate", response_model=SystemThemeOut)
async def activate_theme(
    theme_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Oldin barcha mavzularni faolsizlantiramiz
    await db.execute(update(SystemTheme).values(is_active=False))

    # Tanlangan mavzuni faollashtiramiz
    stmt = select(SystemTheme).where(SystemTheme.id == theme_id)
    result = await db.execute(stmt)
    theme = result.scalars().first()

    if not theme:
        raise HTTPException(status_code=404, detail="Theme topilmadi")

    theme.is_active = True
    await db.commit()
    await db.refresh(theme)
    return theme


# 4. Admin Panel uchun: Barcha mavsumiy effektlarni o'chirish (Default holatga qaytarish)
@router.post("/deactivate-all")
async def deactivate_all_themes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await db.execute(update(SystemTheme).values(is_active=False))
    await db.commit()
    return {"message": "Barcha event effektlari o'chirildi, standart ko'rinishga qaytdi."}