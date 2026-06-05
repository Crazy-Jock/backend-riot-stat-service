import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import quote

from app.repository import player as player_repository
from app.client.riot_client import riot_client
from app.config import config


# сервис для синхронизации актуальных данных игрока
class SyncService(object):
    # функция для синхронизации профиля игрока по riot id, либо обновление riot id игрока в БД
    async def sync_player_by_riot_id(self, game_name: str, tag_line: str, db: AsyncSession) -> dict: # возвращается dict для использования нужных данных в других service функциях
        player_account_data = await riot_client.get(f"https://{quote(config.REGIONAL_HOST["eu"])}.api.riotgames.com/riot/"
                                                    f"account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}")
        
        player = await player_repository.get_player_by_puuid(player_account_data["puuid"], db)
        # если игрок нашелся в БД по puuid, то обновить его riot id
        if player is not None:
            player = await player_repository.update_player_riot_id(player_account_data["puuid"], game_name, tag_line, db)
            return {"player": player}
        
        await self.sync_player_by_puuid(player_account_data["puuid"], db, player_account_data)
    
    # функция для синхронизации профиля игрока по puuid 
    async def sync_player_by_puuid(self, puuid: str, db: AsyncSession, player_account_data=None) -> dict: # возвращается dict для использования нужных данных в других service функциях
        # уменьшение запросов к Riot API, если уже произошла синхронизация по riot id
        if player_account_data is None:
            player_account_data = await riot_client.get(f"https://{quote(config.REGIONAL_HOST["eu"])}.api.riotgames.com/riot/"
                                                        f"account/v1/accounts/by-puuid/{puuid}")
        player_summoner_data = await riot_client.get(f"https://{quote(config.PLATFORM_HOST["euw1"])}.api.riotgames.com/lol/"
                                                     f"summoner/v4/summoners/by-puuid/{puuid}")
        player_summoner_data |= {"region": config.REGIONAL_HOST["eu"]}
        player_ranked_data = await riot_client.get(f"https://{quote(config.PLATFORM_HOST["euw1"])}.api.riotgames.com/lol/"
                                                   f"league/v4/entries/by-puuid/{puuid}")
        
        await player_repository.create_player(player_account_data, player_summoner_data, db)
        await player_repository.create_ranked(puuid, player_ranked_data, db)

    # функция для синхронизации последних n матчей игрока с backfill заполнением
    async def sync_player_matches_by_puuid(self, puuid: str, count: int, db: AsyncSession) -> int:
        player_last_matches_id = await riot_client.get(f"https://{quote(config.REGIONAL_HOST["eu"])}.api.riotgames.com/lol/"
                                                       f"match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}")

        # получаем все уже существующие match_id из БД, чтобы не плодить дубли и уменьшить обращения к Riot API
        existing_matches_id_list = set(await player_repository.get_existing_matches_ids(player_last_matches_id, db))
        new_matches_id = [match_id for match_id in player_last_matches_id if match_id not in existing_matches_id_list]
        # держим id самого свежего матча
        fresh_match_id = player_last_matches_id[0] if player_last_matches_id else None
        # слияние списков в словарь, где new_matches_id ключ для списка c данными матча
        matches_data = await asyncio.gather(*[riot_client.get(f"https://{quote(config.REGIONAL_HOST["eu"])}.api.riotgames.com/lol/"
                                                              f"match/v5/matches/{match_id}") for match_id in new_matches_id])
        await player_repository.create_match(matches_data, db)
        
        player = await player_repository.get_player_by_puuid(puuid, db)
        # если профиль игрока не синхронизирован в БД, то не делать дальнеший backfill последних матчей
        if player is None:
            return len(new_matches_id)
        
        player.count_matches += len(new_matches_id)
        # запись нового свежего id матча после первой синхронизации свежих count матчей
        if player.last_fresh_match_id in player_last_matches_id:
            player.last_fresh_match_id = fresh_match_id

        step = 1
        new_matches_remaining = count - len(new_matches_id)
        # пока не доберемся до last_fresh_match_id из БД, то углубляться только по свежим матчам с шагом count * step
        while new_matches_remaining > 0 and not(player.last_fresh_match_id in player_last_matches_id):
            player_last_matches_id = await riot_client.get(f"https://{quote(config.REGIONAL_HOST["eu"])}.api.riotgames.com/lol/"
                                                           f"match/v5/matches/by-puuid/{puuid}/ids?start={count * step}&count={count}")
            existing_matches_id_list = set(await player_repository.get_existing_matches_ids(player_last_matches_id, db))
            new_matches_id = [match_id for match_id in player_last_matches_id if match_id not in existing_matches_id_list]
            matches_data = await asyncio.gather(*[riot_client.get(f"https://{quote(config.REGIONAL_HOST["eu"])}.api.riotgames.com/lol/"
                                                                  f"match/v5/matches/{match_id}") for match_id in new_matches_id])
            await player_repository.create_match(matches_data, db)
            player.count_matches += len(new_matches_id)
            new_matches_remaining -= len(new_matches_id)
            step += 1

            if fresh_match_id in player_last_matches_id:
                player.last_fresh_match_id = fresh_match_id
                break
        
        # backfill заполнение, когда был найден last_fresh_match_id среди свежих матчей
        while new_matches_remaining > 0 and not(player.backfill_complete):
            player_last_matches_id = await riot_client.get(f"https://{quote(config.REGIONAL_HOST["eu"])}.api.riotgames.com/lol/"
                                                           f"match/v5/matches/by-puuid/{puuid}/ids?start={count * step}&count={count}")
            existing_matches_id_list = set(await player_repository.get_existing_matches_ids(player_last_matches_id, db))
            new_matches_id = [match_id for match_id in player_last_matches_id if match_id not in existing_matches_id_list]
            matches_data = await asyncio.gather(*[riot_client.get(f"https://{quote(config.REGIONAL_HOST["eu"])}.api.riotgames.com/lol/"
                                                                  f"match/v5/matches/{match_id}") for match_id in new_matches_id])                                           
            await player_repository.create_match(matches_data, db)

            player.count_matches += len(new_matches_id)
            new_matches_remaining -= len(new_matches_id)
            if len(player_last_matches_id) == 0:
                player.backfill_complete = True
        
        await db.commit()

        return count - new_matches_remaining
        


sync_service = SyncService()