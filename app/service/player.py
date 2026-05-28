from sqlalchemy.ext.asyncio import AsyncSession

from app.repository import player as player_repository
from app.schemas import PlayerInfoResponse, PlayerRankedResponse
from app.service.sync import sync_service


# функция для вывода данных игрока по riot id
async def get_player_by_riot_id(game_name: str, tag_line: str, db: AsyncSession) -> PlayerInfoResponse:
    player = await player_repository.get_player_by_riot_id(game_name, tag_line, db)

    # если игрока не нашлось в БД по riot id, то производим первую синхронизацию данных
    if player is None:
        player = await sync_service.sync_player_by_riot_id(game_name, tag_line, db)
        player = player.get("player")
    
    return PlayerInfoResponse(puuid=player.puuid,
                              nickname=player.game_name,
                              tag=player.tag_line,
                              profile_icon=player.profile_icon_id,
                              level=player.summoner_lvl,
                              region=player.region)

# функция для вывода данных игрока по puuid
async def get_player_by_puuid(puuid: str, db: AsyncSession) -> PlayerInfoResponse:
    player = await player_repository.get_player_by_puuid(puuid, db)

    # если игрока не нашлось в БД по puuid, то производим первую синхронизацию данных
    if player is None:
        player = await sync_service.sync_player_by_puuid(puuid, db)
        player = player.get("player")

    return PlayerInfoResponse(puuid=player.puuid,
                              nickname=player.game_name,
                              tag=player.tag_line,
                              profile_icon=player.profile_icon_id,
                              level=player.summoner_lvl,
                              region=player.region)

async def get_ranked_entrys(puuid: str, db: AsyncSession) -> PlayerRankedResponse:
    ranked = await player_repository.get_ranked(puuid, db)

    # если не нашелся ранг игрока в БД по puuid, то производим первую синхронизацию данных
    if not ranked:
        return PlayerRankedResponse(puuid=puuid)
    return PlayerRankedResponse(puuid=puuid)