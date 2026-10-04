import jwt as pyjwt
from jwt import PyJWKClient
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from google.oauth2 import id_token
from google.auth.transport import requests

from core.config import settings
from core.session import get_db
from models import User
from schemas.auth import GoogleAuthRequest, AppleAuthRequest, TokenResponse, RefreshTokenRequest
from core.security import create_access_token, create_refresh_token, verify_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

APPLE_PUBLIC_KEY_URL = "https://appleid.apple.com/auth/keys"


# --- 1. GOOGLE OAUTH ENDPOINT ---
@router.post("/google", response_model=TokenResponse)
async def google_auth(body: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    try:
        id_info = id_token.verify_oauth2_token(
            body.token, 
            requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )
        email = id_info.get("email")
        google_id = id_info.get("sub")

        if not email:
            raise HTTPException(status_code=400, detail="Google tokenida email topilmadi")

    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Yaroqsiz Google token")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user:
        user = User(email=email, google_id=google_id)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    elif not user.google_id:
        user.google_id = google_id
        await db.commit()

    access_token = create_access_token({"sub": user.email, "id": user.id})
    refresh_token = create_refresh_token({"sub": user.email, "id": user.id})

    user.refresh_token = refresh_token
    await db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


# --- 2. APPLE SIGN-IN ENDPOINT ---
@router.post("/apple", response_model=TokenResponse)
async def apple_auth(body: AppleAuthRequest, db: AsyncSession = Depends(get_db)):
    try:
        jwks_client = PyJWKClient(APPLE_PUBLIC_KEY_URL)
        signing_key = jwks_client.get_signing_key_from_jwt(body.id_token)

        payload = pyjwt.decode(
            body.id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience="uz.idev.appcentre",
            issuer="https://appleid.apple.com"
        )
        email = payload.get("email")
        apple_id = payload.get("sub")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Yaroqsiz Apple token: {str(e)}")

    # Avval apple_id bo'yicha bazadan qidiramiz
    result = await db.execute(select(User).where(User.apple_id == apple_id))
    user = result.scalars().first()

    # Agar topilmasa va email bo'lsa, email bo'yicha qidiramiz
    if not user and email:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

    if not user:
        if not email:
            raise HTTPException(status_code=400, detail="Birinchi marta kirganda email majburiy")
        user = User(email=email, apple_id=apple_id)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    elif not user.apple_id:
        user.apple_id = apple_id
        await db.commit()

    access_token = create_access_token({"sub": user.email, "id": user.id})
    refresh_token = create_refresh_token({"sub": user.email, "id": user.id})

    user.refresh_token = refresh_token
    await db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


# --- 3. TOKEN ROTATION (REFRESH ENDPOINT) ---
@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = verify_token(body.refresh_token, is_refresh=True)
        user_id = payload.get("id")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Yaroqsiz yoki muddati o'tgan Refresh Token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user or user.refresh_token != body.refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mos kelmadi yoki eskirgan")

    new_access_token = create_access_token({"sub": user.email, "id": user.id})
    new_refresh_token = create_refresh_token({"sub": user.email, "id": user.id})

    user.refresh_token = new_refresh_token
    await db.commit()

    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)