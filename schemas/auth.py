from pydantic import BaseModel


from typing import Optional

class GoogleAuthRequest(BaseModel):
    token: str  # Mobil ilovadan keluvchi Google id_token

class AppleAuthRequest(BaseModel):
    id_token: str  # iOS ilovadan keluvchi Apple identityToken

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

    
class GoogleTokenSchema(BaseModel):
    token: str