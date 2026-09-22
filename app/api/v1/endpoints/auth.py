from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.database import get_db
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut, Token

router = APIRouter()


@router.post(
    "/register", response_model=UserOut, status_code=status.HTTP_201_CREATED
)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Email yoki Telefon raqami unikal ekanligini tekshiramiz
    stmt = select(User).where(
        or_(
            User.email == user_in.email,
            User.phone_number == user_in.phone_number,
        )
    )
    result = await db.execute(stmt)
    existing_user = result.scalars().first()

    if existing_user:
        if existing_user.phone_number == user_in.phone_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ushbu Telefon raqami allaqachon ro'yxatdan o'tgan.",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ushbu Email allaqachon ro'yxatdan o'tgan.",
        )

    # Yangi foydalanuvchi yaratamiz
    new_user = User(
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        email=user_in.email,
        phone_number=user_in.phone_number,
        hashed_password=get_password_hash(user_in.password),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    credentials: UserLogin, db: AsyncSession = Depends(get_db)
):
    # Telefon raqami bo'yicha qidiramiz
    stmt = select(User).where(User.phone_number == credentials.phone_number)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user or not verify_password(
        credentials.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telefon raqami yoki parol xato!",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Token yaratamiz
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}