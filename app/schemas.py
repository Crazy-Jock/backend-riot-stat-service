from pydantic import BaseModel, ConfigDict


# возможно переделаю или удалю
class GetPlayerByNameResponse(BaseModel):
    puuid: str
    tagLine: str
    gameName: str

# схема для вывода данных игрока
class PlayerInfoResponse(BaseModel):
    puuid: str
    nickname: str
    tag: str
    profile_icon: int | None
    level: int | None
    region: str

    model_config = ConfigDict(from_attributes=True)

class PlayerRankedResponse(BaseModel):
    puuid: str