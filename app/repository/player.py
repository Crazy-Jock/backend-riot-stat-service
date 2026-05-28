import json
from re import M

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Player, RankedEntry


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

# получение ранга игрока из БД по puuid
async def get_ranked(puuid: str, db: AsyncSession) -> list:
    result = await db.execute(select(RankedEntry).where(RankedEntry.puuid == puuid))
    ranked = result.scalars().all()
    return ranked

# создание ранга игрока в БД по puuid
async def create_ranked(puuid: str, player_data: list, db: AsyncSession) -> list:
    ranked_list = []
    for data in player_data:
        ranked = RankedEntry(puuid=puuid,
                            queue_type=data["queueType"],
                            tier=data["tier"],
                            rank=data["rank"],
                            wins=data["wins"],
                            looses=data["losses"],
                            league_points=data["leaguePoints"],
                            raw_json=data)
        ranked_list.append(ranked)
        db.add(ranked)
    await db.commit()
    return ranked_list
    