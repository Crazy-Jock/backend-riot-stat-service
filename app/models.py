from datetime import datetime, timezone
from sqlalchemy import JSON, ForeignKey, Integer, String, UniqueConstraint, DateTime
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
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), 
                                                 onupdate=lambda: datetime.now(timezone.utc))
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

class RankedEntry(Base):
    __tablename__ = "ranked_entrys"

    __table_args__ = (UniqueConstraint("puuid", "queue_type"), )

    id: Mapped[int] = mapped_column(primary_key=True)

    puuid: Mapped[str] = mapped_column(ForeignKey("players.puuid", ondelete="CASCADE"), index=True)
    queue_type: Mapped[str] = mapped_column(String(16))
    tier: Mapped[str] = mapped_column(String(16))
    rank: Mapped[str] = mapped_column(String(4))
    wins: Mapped[int] = mapped_column(Integer)
    looses: Mapped[int] = mapped_column(Integer)
    league_points: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)) # хранится, как timestamptz
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                                                 onupdate=lambda: datetime.now(timezone.utc))
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)

    match_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    queue_id: Mapped[int] = mapped_column(Integer)
    game_creation: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True) # хранится, как timestamptz
    game_duration: Mapped[int] # хранится в секундах
    patch: Mapped[str] = mapped_column(String(16))
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

class MatchParticipant(Base):
    __tablename__ = "match_participants"

    __table_args__ = (UniqueConstraint("puuid", "match_id"), )

    id: Mapped[int] = mapped_column(primary_key=True)

    match_id: Mapped[str] = mapped_column(ForeignKey("matches.match_id", ondelete="CASCADE"), index=True)
    game_creation: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True) # хранится, как timestamptz
    game_duration: Mapped[int] # хранится в секундах
    queue_id: Mapped[int] = mapped_column(Integer)
    puuid: Mapped[str] = mapped_column(index=True)
    champion_name: Mapped[str] = mapped_column(String(32))
    kills: Mapped[int] = mapped_column(Integer)
    deaths: Mapped[int] = mapped_column(Integer)
    assists: Mapped[int] = mapped_column(Integer)
    win: Mapped[bool]
    team_position: Mapped[str] = mapped_column(String(16))
    gold: Mapped[int] = mapped_column(Integer)
    creep_score: Mapped[int] = mapped_column(Integer)
    damage: Mapped[int] = mapped_column(Integer)
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)