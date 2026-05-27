from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import quote

from app.repository import player as player_repository
from app.schemas import PlayerFullInfoResponse
from app.service.sync import sync_service
from app.client.riot_client import riot_client
from app.config import config


# функция для вывода данных игрока по riot id
async def get_player_by_riot_id(game_name: str, tag_line: str, db: AsyncSession) -> PlayerFullInfoResponse:
    player = await player_repository.get_player_by_riot_id(game_name, tag_line, db)

    # если игрока не нашлось в БД по riot id, то производим первую синхронизацию данных
    if player is None:
        player = await sync_service.sync_player_by_riot_id(game_name, tag_line, db)
    
    return PlayerFullInfoResponse.model_validate(player)

# функция для вывода данных игрока по puuid
async def get_player_by_puuid(puuid: str, db: AsyncSession) -> PlayerFullInfoResponse:
    player = await player_repository.get_player_by_puuid(puuid, db)

    if player is None:
        player = await sync_service.sync_player_by_puuid(puuid, db)

    return PlayerFullInfoResponse.model_validate(player)