import time

from sqlalchemy import JSON, ForeignKey, String
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

    created_at: Mapped[int] = mapped_column(default=lambda: int(time.time())) # хранится, как timestamp в секундах
    updated_at: Mapped[int] = mapped_column(default=lambda: int(time.time()))
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

class RankedEntry(Base):
    __tablename__ = "ranked_entrys"

    id: Mapped[int] = mapped_column(primary_key=True)

    puuid: Mapped[str] = mapped_column(ForeignKey("players.puuid", ondelete="CASCADE"))