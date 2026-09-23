from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class SystemThemeCreate(BaseModel):
    theme_name: str
    effect_type: Optional[str] = "snowfalling"
    effect_config: Optional[Dict[str, Any]] = {
        "intensity": "medium",
        "speed": 1.5,
        "particle_color": "#FFFFFF",
    }
    banner_url: Optional[str] = None
    primary_color: Optional[str] = "#E53935"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class SystemThemeOut(BaseModel):
    id: str
    theme_name: str
    is_active: bool
    effect_type: Optional[str]
    effect_config: Optional[Dict[str, Any]]
    banner_url: Optional[str]
    primary_color: Optional[str]

    class Config:
        from_attributes = True