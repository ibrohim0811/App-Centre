import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class SystemTheme(Base):
    __tablename__ = "system_themes"

    id: Mapped[str] = mapped_column(
        String, primary_primary_key=True, default=lambda: str(uuid.uuid4())
    )
    theme_name: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # masalan: 'new_year', 'spring_navruz', 'default'
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=False
    )  # Hozirda faolmi?

    # Visual Effects Sozlamalari
    effect_type: Mapped[str] = mapped_column(
        String(50), nullable=True
    )  # 'snowfalling', 'fireworks', 'confetti', 'none'
    effect_config: Mapped[dict] = mapped_column(
        JSON,
        default={
            "intensity": "medium",  # snowfall tezligi va zichligi
            "particle_color": "#FFFFFF",
            "speed": 1.5,
        },
        nullable=True,
    )

    # Event Banner va Assetlar
    banner_url: Mapped[str] = mapped_column(String, nullable=True)
    primary_color: Mapped[str] = mapped_column(
        String(20), nullable=True
    )  # Masalan: #FF0000 (Yangi yil qizil rangi)

    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)