from datetime import datetime, timezone
from sqlalchemy import JSON, ForeignKey, String, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)

    puuid: Mapped[str] = mapped_column(String(78), unique=True, index=True)
    game_name: Mapped[str] = mapped_column(String(64))
    tag_line: Mapped[str] = mapped_column(String(32))
    profile_icon_id: Mapped[int | None] = mapped_column(default=None)
    summoner_lvl: Mapped[int | None] = mapped_column(default=None)
    region: Mapped[str] =  mapped_column(String(32))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)) # хранится, как timestamptz
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

class RankedEntry(Base):
    __tablename__ = "ranked_entrys"

    __table_args__ = (UniqueConstraint("puuid", "queue_type"), )

    id: Mapped[int] = mapped_column(primary_key=True)

    puuid: Mapped[str] = mapped_column(ForeignKey("players.puuid", ondelete="CASCADE"), index=True)
    queue_type: Mapped[str] = mapped_column(String(16))
    tier: Mapped[str] = mapped_column(String(16))
    rank: Mapped[str] = mapped_column(String(4))
    wins: Mapped[int]
    looses: Mapped[int]
    league_points: Mapped[int]

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)) # хранится, как timestamptz
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)