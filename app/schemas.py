from pydantic import BaseModel


class GetPlayerByNameResponse(BaseModel):
    puuid: str
    tagLine: str
    gameName: str

    