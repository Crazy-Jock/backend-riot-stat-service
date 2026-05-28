from sqlalchemy import select
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.models import Match, MatchParticipant, Player, RankedEntry


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

# создание нового игрока в БД или обновление профиля игрока в БД
async def create_player(player_account_data: dict, player_summoner_data: dict, db: AsyncSession):
    stmt = insert(Player).values(puuid=player_account_data["puuid"], 
                                 game_name=player_account_data["gameName"],
                                 tag_line=player_account_data["tagLine"],
                                 profile_icon_id=player_summoner_data["profileIconId"],
                                 summoner_lvl=player_summoner_data["summonerLevel"],
                                 region=player_summoner_data["region"],
                                 raw_json=player_account_data | player_summoner_data)
    stmt = stmt.on_conflict_do_update(index_elements=["puuid"], set_={"game_name": player_account_data["gameName"],
                                                                     "tag_line": player_account_data["tagLine"],
                                                                     "profile_icon_id": player_summoner_data["profileIconId"],
                                                                     "summoner_lvl": player_summoner_data["summonerLevel"],
                                                                     "region": player_summoner_data["region"],
                                                                     "raw_json": player_account_data | player_summoner_data})
    await db.execute(stmt)
    await db.commit()

# обновление game name и tag line игрока по puuid в БД
async def update_player_riot_id(puuid: str, game_name: str, tag_line: str, db: AsyncSession) -> Player:
    result = await db.execute(select(Player).where(Player.puuid == puuid))
    player = result.scalar_one_or_none()
    player.game_name = game_name
    player.tag_line = tag_line
    await db.commit()
    return player

# получение ранга игрока из БД по puuid
async def get_ranked(puuid: str, db: AsyncSession) -> list[RankedEntry]:
    result = await db.execute(select(RankedEntry).where(RankedEntry.puuid == puuid))
    ranked = result.scalars().all()
    return ranked

# создание ранга игрока в БД по puuid или обновление ранга игрока в БД
async def create_ranked(puuid: str, player_data: list, db: AsyncSession):
    for data in player_data:
        # при повторной синхронизации, чтобы не плодить дубли
        stmt = insert(RankedEntry).values(puuid=puuid,
                                          queue_type=data["queueType"],
                                          tier=data["tier"],
                                          rank=data["rank"],
                                          wins=data["wins"],
                                          looses=data["losses"],
                                          league_points=data["leaguePoints"],
                                          raw_json=data)
        stmt = stmt.on_conflict_do_update(index_elements=["puuid", "queue_type"],
                                          set_={"tier": data["tier"],
                                               "rank": data["rank"],
                                               "wins": data["wins"],
                                               "looses": data["losses"],
                                               "league_points": data["leaguePoints"],
                                               "raw_json": data})

        await db.execute(stmt)

    await db.commit()

# функция для получения списка матчей игрока по puuid
async def get_player_matches(puuid: str, db: AsyncSession) -> list[MatchParticipant]:
    result = await db.execute(select(MatchParticipant).where(MatchParticipant.puuid == puuid).order_by(MatchParticipant.game_creation.desc()))
    player_matches = result.scalars().all()
    return player_matches

# функция создания матча и создания игроков матча
async def create_match(match_data_list: dict, db: AsyncSession) -> list[Match]:
    match_list = []
    parcipant_list = []
    for match_data in match_data_list:
        match = Match(match_id=match_data["metadata"]["matchId"],
                      queue_id=match_data["info"]["queueId"],
                      game_creation=datetime.fromtimestamp(match_data["info"]["gameCreation"] / 1000, tz=timezone.utc),
                      game_duration=match_data["info"]["gameDuration"],
                      patch=".".join(match_data["info"]["gameVersion"].split(".")[:2]),
                      raw_json=match_data)
        match_list.append(match)

        for parcipant_data in match_data["info"]["participants"]:
            parcipant = MatchParticipant(match_id=match_data["metadata"]["matchId"],
                                       game_creation=datetime.fromtimestamp(match_data["info"]["gameCreation"] / 1000, tz=timezone.utc),
                                       game_duration=match_data["info"]["gameDuration"],
                                       queue_id=match_data["info"]["queueId"],
                                       puuid=parcipant_data["puuid"],
                                       champion_name=parcipant_data["championName"],
                                       kills=parcipant_data["kills"],
                                       deaths=parcipant_data["deaths"],
                                       assists=parcipant_data["assists"],
                                       win=parcipant_data["win"],
                                       team_position=parcipant_data["teamPosition"],
                                       gold=parcipant_data["goldEarned"],
                                       creep_score=parcipant_data["totalMinionsKilled"],
                                       damage=parcipant_data["totalDamageDealtToChampions"],
                                       raw_json=parcipant_data)
            parcipant_list.append(parcipant)

    db.add_all(match_list)
    db.add_all(parcipant_list)
    await db.commit()

    return match_list

# функция для получения списка уже существующих match_id в БД
async def get_existing_matches_ids(matches_id_list: list[str], db: AsyncSession) -> list[str]:
    # если вдруг попадет пустой список
    if not matches_id_list:
        return []
    
    result = await db.execute(select(Match.match_id).where(Match.match_id.in_(matches_id_list)))
    existing_matches_id_list = result.scalars().all()
    return list(existing_matches_id_list)

# функция для получения матча по match id
async def get_match_by_match_id(match_id: int, db: AsyncSession) -> Match:
    result = await db.execute(select(Match).where(Match.match_id == match_id))
    match = result.scalar_one_or_none()
    return match

# функция для получения списка игроков матча по match id
async def get_participants_by_match_id(match_id: int, db: AsyncSession) -> list[MatchParticipant]:
    result = await db.execute(select(MatchParticipant).where(MatchParticipant.match_id == match_id))
    player_matches = result.scalars().all()
    return player_matches

# функция для получения всех матчей по puuid игрока и по имени чемпиона
async def get_player_champion_matches(puuid: str, champion_name: str, db: AsyncSession) -> list[MatchParticipant]:
    result = await db.execute(select(MatchParticipant).where(MatchParticipant.puuid == puuid, MatchParticipant.champion_name.ilike(champion_name)))
    player_champion_matches = result.scalars().all()
    return player_champion_matches