import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class Podcast(Base):
    __tablename__ = "podcasts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255))
    document_ids: Mapped[str] = mapped_column(Text)  # JSON list of document IDs
    provider_id: Mapped[str] = mapped_column(String(50))
    speakers: Mapped[str] = mapped_column(Text)  # JSON list of speaker configs
    language: Mapped[str] = mapped_column(String(10), default="en")

    summary: Mapped[str | None] = mapped_column(String(300), nullable=True)
    script: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    num_speakers: Mapped[int] = mapped_column(Integer, default=2)
    podbean_episode_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
