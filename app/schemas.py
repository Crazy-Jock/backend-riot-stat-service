from datetime import datetime
from typing import Union
from pydantic import BaseModel, field_serializer


# схема для вывода данных игрока
class PlayerInfoResponse(BaseModel):
    puuid: str
    nickname: str
    tag: str
    profile_icon: int | None
    level: int | None
    region: str

class PlayerRankedEntrys(BaseModel):
    queue: str
    tier: str
    division: str
    lp: int
    win_rate: float
    wins: int
    looses: int

class PlayerRankedResponse(BaseModel):
    puuid: str
    nickname: str
    tag: str
    profile_icon: int | None
    rank: list[PlayerRankedEntrys]

class ParticipantBase(BaseModel):
    puuid: str
    champion: str
    win: bool

    @field_serializer("win")
    def serialize_win(self, value: bool) -> str:
        if value:
            return "Победа"
        else:
            return "Поражение"

class SoloqFlexParticipant(ParticipantBase):
    kills: int
    deaths: int
    assists: int
    kda: float
    position: str
    cs: int
    damage_to_champions: int


class AramParticipant(ParticipantBase):
    kda: float
    damage_to_champions: int

class NormalParticipant(ParticipantBase):
    kda: float
    position: str
    cs_per_minute: float
    gold_per_minute: float
    damage_to_champions_per_minute: float

class ClashParticipant(ParticipantBase):
    kills: int
    deaths: int
    assists: int
    kda: float
    position: str
    cs: int
    cs_per_minute: float
    gold: int
    gold_per_minute: float
    damage_to_champions: int

class ArenaParticipant(ParticipantBase):
    kills: int
    deaths: int
    assists: int
    kda: float
    damage_to_champions: int

class ParcipantMatchInfo(BaseModel):
    match_id: str
    queue: str
    created_at: datetime
    duration: int

    participant: Union[SoloqFlexParticipant, AramParticipant,
                       NormalParticipant, ClashParticipant,
                       ArenaParticipant]

    @field_serializer("duration")
    def serialize_duration(self, value: int) -> str:
        return f"{value // 60} мин {value % 60} сек"

class PlayerLastMatchesResponse(BaseModel):
    matches: list[ParcipantMatchInfo]

class MatchInfoResponse(BaseModel):
    match_id: str
    queue: str
    created_at: datetime
    duration: int
    patch: str

    participants: list[Union[SoloqFlexParticipant, AramParticipant,
                             NormalParticipant, ClashParticipant,
                             ArenaParticipant]]
    
    @field_serializer("duration")
    def serialize_duration(self, value: int) -> str:
        return f"{value // 60} мин {value % 60} сек"
    
class ChampionStatResponse(BaseModel):
    champion: str
    matches: int
    wins: int
    looses: int
    winrate: float