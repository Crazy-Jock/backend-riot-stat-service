from pydantic import BaseModel, ConfigDict


# схема для вывода данных игрока
class PlayerInfoResponse(BaseModel):
    puuid: str
    nickname: str
    tag: str
    profile_icon: int | None
    level: int | None
    region: str

    model_config = ConfigDict(from_attributes=True)

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