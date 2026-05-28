import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import quote

from app.models import Player
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
        player_matches_id = await riot_client.get(f"https://{quote(config.REGIONAL_HOST["eu"])}.api.riotgames.com/lol/"
                                                   f"match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20")

        existing_matches_id_list = set(await player_repository.get_existing_matches_ids(player_matches_id, db))
        new_matches_id = list(set(player_matches_id) - existing_matches_id_list)
        # слияние списков в словарь, где new_matches_id ключ для списка c данными матча
        matches_data = dict(zip(new_matches_id, await asyncio.gather(*[riot_client.get(f"https://{quote(config.REGIONAL_HOST["eu"])}.api.riotgames.com/lol/"
                                                                                       f"match/v5/matches/{match_id}") for match_id in new_matches_id])))
        
        await player_repository.create_player(player_account_data, player_summoner_data, db)
        await player_repository.create_ranked(puuid, player_ranked_data, db)

    # функция для синхронизации последних n матчей игрока
    async def sync_player_matches_by_puuid(self, puuid: str, count: int, db: AsyncSession):
        player_last_matches_id = await riot_client.get(f"https://{quote(config.REGIONAL_HOST["eu"])}.api.riotgames.com/lol/"
                                                       f"match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}")

        existing_matches_id_list = set(await player_repository.get_existing_matches_ids(player_last_matches_id, db))
        new_matches_id = list(set(player_last_matches_id) - existing_matches_id_list)
        # слияние списков в словарь, где new_matches_id ключ для списка c данными матча
        matches_data = await asyncio.gather(*[riot_client.get(f"https://{quote(config.REGIONAL_HOST["eu"])}.api.riotgames.com/lol/"
                                                              f"match/v5/matches/{match_id}") for match_id in new_matches_id])
        await player_repository.create_match(matches_data, db)


sync_service = SyncService()