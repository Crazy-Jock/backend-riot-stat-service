import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Player


# получение игрока из БД по riot id (game name и tag line)
async def get_player_by_riot_id(game_name: str, tag_line: str, db: AsyncSession) -> Player | None:
    result = await db.execute(select(Player).where(Player.game_name == game_name, Player.tag_line == tag_line))
    player = result.scalar_one_or_none()
    return player

# получение игрока из БД по puuid
async def get_player_by_puuid(puuid: str, db: AsyncSession) -> Player | None:
    result = await db.execute(select(Player).where(Player.puuid == puuid))
    player = result.scalar_one_or_none()
    return player

# создание нового игрока в БД
async def create_player(player_account_data: dict, player_summoner_data: dict, db: AsyncSession) -> Player:
    player = Player(puuid=player_account_data["puuid"], 
                    game_name=player_account_data["gameName"],
                    tag_line=player_account_data["tagLine"],
                    profile_icon_id=player_summoner_data["profileIconId"],
                    summoner_lvl=player_summoner_data["summonerLevel"],
                    region=player_summoner_data["region"],
                    raw_json=player_account_data | player_summoner_data)
    db.add(player)
    await db.commit()
    return player

# обновление game name и tag line игрока по puuid в БД
async def update_player_riot_id(puuid: str, game_name: str, tag_line: str, db: AsyncSession) -> Player:
    result = await db.execute(select(Player).where(Player.puuid == puuid))
    player = result.scalar_one_or_none()
    player.game_name = game_name
    player.tag_line = tag_line
    await db.commit()
    return player