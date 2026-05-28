from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository import player as player_repository
from app.schemas import AramParticipant, ArenaParticipant, ClashParticipant, MatchInfoResponse, NormalParticipant, ParcipantMatchInfo, PlayerInfoResponse, PlayerLastMatchesResponse, PlayerRankedEntrys, PlayerRankedResponse, SoloqFlexParticipant
from app.service.sync import sync_service
from app.constants import QUEUE_MAPPING_HELPER


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

# функция для получения ранга игрока по puuid
async def get_ranked_entrys(puuid: str, db: AsyncSession) -> PlayerRankedResponse:
    ranked_list = await player_repository.get_ranked(puuid, db)
    mapping_helper = {"RANKED_SOLO_5x5": "soloq", "RANKED_FLEX_SR": "flex"} # для облегчения формирования response модели
   
    # если не нашелся ранг игрока в БД по puuid, то производим первую синхронизацию данных
    if not ranked_list:
        ranked_list = await sync_service.sync_player_by_puuid(puuid, db)
        ranked_list = ranked_list.get("ranked")
    
    player = await player_repository.get_player_by_puuid(puuid, db)

    return PlayerRankedResponse(puuid=puuid,
                                nickname=player.game_name,
                                tag=player.tag_line,
                                profile_icon=player.profile_icon_id,
                                rank=[PlayerRankedEntrys(
                                    queue=mapping_helper[rank.queue_type],
                                    tier=rank.tier,
                                    division=rank.rank,
                                    lp=rank.league_points,
                                    win_rate=round(rank.wins / (rank.wins + rank.looses) * 100, 2),
                                    wins=rank.wins,
                                    looses=rank.looses)
                                    for rank in ranked_list])

# функция для получения списка матчей игрока по puuid
async def get_player_matches(puuid: str, db: AsyncSession) -> PlayerLastMatchesResponse:
    player_matches_list = await player_repository.get_player_matches(puuid, db)

    if not player_matches_list:
        await sync_service.sync_player_matches_by_puuid(puuid, 20, db)

    # список схем для составления финальной response схемы
    player_matches_list_schemas = []
    for player_match in player_matches_list:
        if player_match.queue_id == 420 or player_match.queue_id == 440:
            player_matches_list_schemas.append(ParcipantMatchInfo(match_id=player_match.match_id,
                                                                  queue=QUEUE_MAPPING_HELPER[player_match.queue_id],
                                                                  created_at=player_match.game_creation,
                                                                  duration=player_match.game_duration,
                                                                  participant=SoloqFlexParticipant(puuid=puuid,
                                                                                                   champion=player_match.champion_name,
                                                                                                   win=player_match.win,
                                                                                                   kills=player_match.kills,
                                                                                                   deaths=player_match.deaths,
                                                                                                   assists=player_match.assists,
                                                                                                   kda=round((player_match.kills + 
                                                                                                              player_match.assists) / 
                                                                                                              max(player_match.deaths, 1), 2),
                                                                                                   position=player_match.team_position,
                                                                                                   cp=player_match.creep_score,
                                                                                                   damage_to_champions=player_match.damage)))
        elif player_match.queue_id == 450:
            player_matches_list_schemas.append(ParcipantMatchInfo(match_id=player_match.match_id,
                                                                  queue=QUEUE_MAPPING_HELPER[player_match.queue_id],
                                                                  created_at=player_match.game_creation,
                                                                  duration=player_match.game_duration,
                                                                  participant=AramParticipant(puuid=puuid,
                                                                                              champion=player_match.champion_name,
                                                                                              win=player_match.win,
                                                                                              kda=round((player_match.kills + 
                                                                                                         player_match.assists) / 
                                                                                                         max(player_match.deaths, 1), 2),
                                                                                              damage_to_champions=player_match.damage)))
        elif player_match.queue_id == 400 or player_match.queue_id == 430:
            player_matches_list_schemas.append(ParcipantMatchInfo(match_id=player_match.match_id,
                                                                  queue=QUEUE_MAPPING_HELPER[player_match.queue_id],
                                                                  created_at=player_match.game_creation,
                                                                  duration=player_match.game_duration,
                                                                  participant=NormalParticipant(puuid=puuid,
                                                                                                champion=player_match.champion_name,
                                                                                                win=player_match.win,
                                                                                                kda=round((player_match.kills + 
                                                                                                           player_match.assists) / 
                                                                                                           max(player_match.deaths, 1), 2),
                                                                                                position=player_match.team_position,
                                                                                                cp_per_minute=round(player_match.creep_score / 
                                                                                                                    player_match.game_duration * 60, 2),
                                                                                                gold_per_minute=round(player_match.gold / 
                                                                                                                      player_match.game_duration * 60, 2),
                                                                                                damage_to_champions_per_minute=round(player_match.damage /
                                                                                                                                     player_match.game_duration * 
                                                                                                                                     60, 2))))
        elif player_match.queue_id == 700:
            player_matches_list_schemas.append(ParcipantMatchInfo(match_id=player_match.match_id,
                                                                  queue=QUEUE_MAPPING_HELPER[player_match.queue_id],
                                                                  created_at=player_match.game_creation,
                                                                  duration=player_match.game_duration,
                                                                  participant=ClashParticipant(puuid=puuid,
                                                                                               champion=player_match.champion_name,
                                                                                               win=player_match.win,
                                                                                               kills=player_match.kills,
                                                                                               deaths=player_match.deaths,
                                                                                               assists=player_match.assists,
                                                                                               kda=round((player_match.kills + 
                                                                                                          player_match.assists) / 
                                                                                                          max(player_match.deaths, 1), 2),
                                                                                               position=player_match.team_position,
                                                                                               cp=player_match.creep_score,
                                                                                               cp_per_minute=round(player_match.creep_score / 
                                                                                                                   player_match.game_duration * 60, 2),
                                                                                               gold=player_match.gold,
                                                                                               gold_per_minute=round(player_match.gold / 
                                                                                                                     player_match.game_duration * 60, 2),
                                                                                               damage_to_champions=player_match.damage)))
        elif player_match.queue_id == 1700:
            player_matches_list_schemas.append(ParcipantMatchInfo(match_id=player_match.match_id,
                                                                  queue=QUEUE_MAPPING_HELPER[player_match.queue_id],
                                                                  created_at=player_match.game_creation,
                                                                  duration=player_match.game_duration,
                                                                  participant=ArenaParticipant(puuid=puuid,
                                                                                               champion=player_match.champion_name,
                                                                                               win=player_match.win,
                                                                                               kills=player_match.kills,
                                                                                               deaths=player_match.deaths,
                                                                                               assists=player_match.assists,
                                                                                               kda=round((player_match.kills + 
                                                                                                          player_match.assists) / 
                                                                                                          max(player_match.deaths, 1), 2),
                                                                                               damage_to_champions=player_match.damage)))
        else:
            raise HTTPException(
                status_code=400,
                detail="Появился неизвестный queue_id={player_match.queue_id}"
            )

    return PlayerLastMatchesResponse(matches=player_matches_list_schemas)

# функция для получения матча по match_id и его игроков
async def get_match_by_match_id(match_id: int, db: AsyncSession) -> MatchInfoResponse:
    match = await player_repository.get_match_by_match_id(match_id, db)

    # проверяем наличие матча в БД
    if match is None:
        raise HTTPException(
            status_code=404,
            detail=f"Матч {match_id} не найден или не существует"
        )
    
    participant_list_schemas = []
    participant_list = await player_repository.get_participants_by_match_id(match_id, db)
    for participant in participant_list:
        if match.queue_id == 420 or match.queue_id == 440:
            participant_list_schemas.append(SoloqFlexParticipant(puuid=participant.puuid,
                                                                 champion=participant.champion_name,
                                                                 win=participant.win,
                                                                 kills=participant.kills,
                                                                 deaths=participant.deaths,
                                                                 assists=participant.assists,
                                                                 kda=round((participant.kills + 
                                                                            participant.assists) / 
                                                                            max(participant.deaths, 1), 2),
                                                                 position=participant.team_position,
                                                                 cp=participant.creep_score,
                                                                 damage_to_champions=participant.damage))
        elif match.queue_id == 450:
            participant_list_schemas.append(AramParticipant(puuid=participant.puuid,
                                                            champion=participant.champion_name,
                                                            win=participant.win,
                                                            kda=round((participant.kills + 
                                                                       participant.assists) / 
                                                                       max(participant.deaths, 1), 2),
                                                            damage_to_champions=participant.damage))
        elif match.queue_id == 400 or match.queue_id == 430:
            participant_list_schemas.append(NormalParticipant(puuid=participant.puuid,
                                                              champion=participant.champion_name,
                                                              win=participant.win,
                                                              kda=round((participant.kills + 
                                                                          participant.assists) / 
                                                                          max(participant.deaths, 1), 2),
                                                              position=participant.team_position,
                                                              cp_per_minute=round(participant.creep_score / 
                                                                                  participant.game_duration * 60, 2),
                                                              gold_per_minute=round(participant.gold / 
                                                                                    participant.game_duration * 60, 2),
                                                              damage_to_champions_per_minute=round(participant.damage /
                                                                                                   participant.game_duration * 
                                                                                                   60, 2)))
        elif match.queue_id == 700:
            participant_list_schemas.append(ClashParticipant(puuid=participant.puuid,
                                                             champion=participant.champion_name,
                                                             win=participant.win,
                                                             kills=participant.kills,
                                                             deaths=participant.deaths,
                                                             assists=participant.assists,
                                                             kda=round((participant.kills + 
                                                                        participant.assists) / 
                                                                        max(participant.deaths, 1), 2),
                                                             position=participant.team_position,
                                                             cp=participant.creep_score,
                                                             cp_per_minute=round(participant.creep_score / 
                                                                                 participant.game_duration * 60, 2),
                                                              gold=participant.gold,
                                                              gold_per_minute=round(participant.gold / 
                                                                                    participant.game_duration * 60, 2),
                                                              damage_to_champions=participant.damage))
        elif match.queue_id == 1700:
            participant_list_schemas.append(ArenaParticipant(puuid=participant.puuid,
                                                             champion=participant.champion_name,
                                                             win=participant.win,
                                                             kills=participant.kills,
                                                             deaths=participant.deaths,
                                                             assists=participant.assists,
                                                             kda=round((participant.kills + 
                                                                        participant.assists) / 
                                                                        max(participant.deaths, 1), 2),
                                                             damage_to_champions=participant.damage))
        else:
            raise HTTPException(
                status_code=400,
                detail="Появился неизвестный queue_id={player_match.queue_id}"
            )
        
    return MatchInfoResponse(match_id=match.match_id,
                             queue=QUEUE_MAPPING_HELPER[match.queue_id],
                             created_at=match.game_creation,
                             duration=match.game_duration,
                             patch=match.patch,
                             participants=participant_list_schemas)