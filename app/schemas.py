from pydantic import BaseModel, ConfigDict


# возможно переделаю или удалю
class GetPlayerByNameResponse(BaseModel):
    puuid: str
    tagLine: str
    gameName: str

# схема для вывода данных игрока
class PlayerFullInfoResponse(BaseModel):
    puuid: str
    game_name: str
    tag_line: str
    profile_icon_id: int | None
    summoner_lvl: int | None
    region: str

    model_config = ConfigDict(from_attributes=True)